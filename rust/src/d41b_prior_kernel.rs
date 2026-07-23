//! Compact exact D40 prior plus the reserved zero-residual actor kernel.

pub const FEATURES: usize = 44;
pub const CELLS: i32 = 11 * 22;
pub const TOTAL_TURNS: i32 = 300;
pub const MAX_WORKERS: i32 = 3;
pub const RESIDUAL_HIDDEN: usize = 16;
pub const RESIDUAL_PARAMETERS: usize =
    FEATURES * RESIDUAL_HIDDEN + RESIDUAL_HIDDEN + RESIDUAL_HIDDEN + 1;

fn scaled(value: f32, scale: i32) -> i32 {
    (value * scale as f32).round() as i32
}

fn kind(row: &[f32; FEATURES]) -> i32 {
    (0..6)
        .max_by(|left, right| row[20 + *left].total_cmp(&row[20 + *right]))
        .expect("nonempty job-kind range") as i32
}

fn option_cell(spatial: Option<i32>) -> (i32, i32, i32) {
    spatial.map_or((0, 0, 0), |cell| (1, cell % 22, cell / 22))
}

fn target(job_kind: i32, action: i32) -> (i32, i32, i32) {
    option_cell((job_kind > 1).then_some(action % CELLS))
}

fn plant(row: &[f32; FEATURES]) -> (i32, i32, i32) {
    option_cell((row[43] >= 0.0).then(|| scaled(row[43], CELLS - 1)))
}

/// Return candidate indexes in exact-prior order, with D40's action first.
pub fn exact_prior_order(features: &[[f32; FEATURES]], actions: &[i32], branch: u8) -> Vec<usize> {
    assert!(!actions.is_empty() && actions.len() == features.len());
    assert!(branch < 4);
    let mut indexes: Vec<usize> = (0..actions.len()).collect();
    match branch {
        0 => {
            let turn = scaled(features[0][1], TOTAL_TURNS);
            let workers = scaled(features[0][2], MAX_WORKERS);
            let goal = if turn > TOTAL_TURNS - 30 || workers >= MAX_WORKERS {
                0
            } else if workers < 2 {
                1
            } else {
                2
            };
            indexes.sort_by_key(|&index| {
                let plane = actions[index] / CELLS;
                (i32::from(plane != goal), plane, actions[index])
            });
        }
        1 => indexes.sort_by_key(|&index| {
            let row = &features[index];
            let job_kind = kind(row);
            let reduction = scaled(row[28], 20);
            if reduction > 0 {
                (
                    0,
                    -reduction,
                    scaled(row[26], TOTAL_TURNS),
                    i32::from(job_kind != 1),
                    job_kind,
                    target(job_kind, actions[index]),
                    plant(row),
                    actions[index],
                )
            } else {
                (1, 0, 0, 0, 0, (0, 0, 0), (0, 0, 0), actions[index])
            }
        }),
        2 => indexes.sort_by_key(|&index| {
            let row = &features[index];
            let job_kind = kind(row);
            if job_kind != 0 {
                (
                    0,
                    scaled(row[26], TOTAL_TURNS),
                    job_kind,
                    target(job_kind, actions[index]),
                    plant(row),
                    actions[index],
                )
            } else {
                (1, 0, 0, (0, 0, 0), (0, 0, 0), actions[index])
            }
        }),
        3 => indexes.sort_by_key(|&index| {
            let row = &features[index];
            let job_kind = kind(row);
            (
                -scaled(row[29], 50_000),
                scaled(row[26], TOTAL_TURNS),
                job_kind,
                target(job_kind, actions[index]),
                actions[index],
            )
        }),
        _ => unreachable!(),
    }
    indexes
}

#[derive(Clone)]
pub struct ResidualWeights {
    pub input: [[f32; FEATURES]; RESIDUAL_HIDDEN],
    pub hidden_bias: [f32; RESIDUAL_HIDDEN],
    pub output: [f32; RESIDUAL_HIDDEN],
    pub output_bias: f32,
}

impl Default for ResidualWeights {
    fn default() -> Self {
        Self {
            input: [[0.0; FEATURES]; RESIDUAL_HIDDEN],
            hidden_bias: [0.0; RESIDUAL_HIDDEN],
            output: [0.0; RESIDUAL_HIDDEN],
            output_bias: 0.0,
        }
    }
}

pub fn logits(
    features: &[[f32; FEATURES]],
    actions: &[i32],
    branch: u8,
    temperature: f32,
    weights: &ResidualWeights,
) -> Vec<f32> {
    assert!(temperature.is_finite() && temperature > 0.0);
    let order = exact_prior_order(features, actions, branch);
    let mut rank = vec![0usize; order.len()];
    for (position, &candidate) in order.iter().enumerate() {
        rank[candidate] = position;
    }
    features
        .iter()
        .enumerate()
        .map(|(candidate, row)| {
            let mut residual = weights.output_bias;
            for hidden in 0..RESIDUAL_HIDDEN {
                let mut activation = weights.hidden_bias[hidden];
                for input in 0..FEATURES {
                    activation += weights.input[hidden][input] * row[input];
                }
                residual += weights.output[hidden] * activation.max(0.0);
            }
            -(rank[candidate] as f32) * temperature + residual
        })
        .collect()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn zero_residual_keeps_exact_prior_argmax() {
        let mut features = vec![[0.0; FEATURES]; 3];
        features[0][22] = 1.0;
        features[1][21] = 1.0;
        features[2][23] = 1.0;
        features[0][28] = 3.0 / 20.0;
        features[1][28] = 3.0 / 20.0;
        features[2][28] = 2.0 / 20.0;
        features[0][26] = 2.0 / 300.0;
        features[1][26] = 2.0 / 300.0;
        features[2][26] = 1.0 / 300.0;
        features.iter_mut().for_each(|row| row[43] = -1.0);
        let actions = vec![5 * CELLS + 3, 4 * CELLS, 6 * CELLS + 2];
        let order = exact_prior_order(&features, &actions, 1);
        assert_eq!(order[0], 1);
        let scores = logits(&features, &actions, 1, 1.0, &ResidualWeights::default());
        let selected = (0..scores.len())
            .max_by(|left, right| scores[*left].total_cmp(&scores[*right]))
            .unwrap();
        assert_eq!(selected, order[0]);
        assert_eq!(RESIDUAL_PARAMETERS, 737);
    }
}
