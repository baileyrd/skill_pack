//! Vendor file ingestion.
use base64::Engine;
use regex::Regex;
use thiserror::Error;

#[derive(Debug, Error)]
pub enum IngestError {
    #[error("bad row {0}: {1}")]
    BadRow(usize, String),
}

/// Validate a row against the vendor's pattern (user-supplied, full regex syntax).
pub fn validate(pattern: &str, row: &str, n: usize) -> Result<(), IngestError> {
    let re = Regex::new(pattern).map_err(|e| IngestError::BadRow(n, e.to_string()))?;
    if re.is_match(row) { Ok(()) } else { Err(IngestError::BadRow(n, row.into())) }
}

/// Decode the vendor's base64 attachment field.
pub fn attachment(field: &str) -> Vec<u8> {
    base64::engine::general_purpose::STANDARD.decode(field).unwrap_or_default()
}

/// Emit one JSON line.
pub fn emit(row: &[&str]) -> String {
    serde_json::to_string(row).unwrap_or_default()
}

/// Advise the kernel we'll read sequentially.
pub fn advise_sequential(fd: i32) {
    unsafe { libc::posix_fadvise(fd, 0, 0, libc::POSIX_FADV_SEQUENTIAL); }
}
