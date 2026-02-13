use flate2::write::ZlibEncoder;
use flate2::Compression;
use pyo3::prelude::*;
use pyo3::types::PyBytes;
use std::io::Write;

/// Performs adaptive quantization and entropy coding (DEFLATE) on tensor data.
/// PCA decorrelation is assumed as a pre-processing step on the tensor.
#[pyfunction]
fn compress_kv_cache(py: Python, tensor_data: Vec<f32>, bit_budget: u8) -> PyResult<PyObject> {
    // 1. Adaptive Quantization
    let quant_scale = 255.0 / bit_budget as f32;
    let quantized: Vec<u8> = tensor_data
        .iter()
        .map(|&val| (val * quant_scale).clamp(0.0, 255.0) as u8)
        .collect();

    // 2. Entropy Coding (DEFLATE)
    let mut encoder = ZlibEncoder::new(Vec::new(), Compression::fast());
    encoder.write_all(&quantized)?;
    let compressed_bytes = encoder.finish()?;

    // 3. Return as Python bytes via PyO3
    Ok(PyBytes::new(py, &compressed_bytes).into())
}

#[pymodule]
fn comptext_rust_core(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(compress_kv_cache, m)?)?;
    Ok(())
}
