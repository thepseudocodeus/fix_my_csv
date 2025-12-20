use rustler::{Env, Error, Binary, OwnedBinary};
use std::borrow::Cow;
// use rustler::NifResult;


/// Remove null bytes from binary
fn remove_null_bytes<'a>(env: Env<'a>, input: Binary) -> Result<Binary<'a>, Error> {
    let cleaned: Vec<u8> = input.as_slice().iter().copied().filter(|&b| b != 0).collect();
    let mut binary = OwnedBinary::new(cleaned.len())
        .ok_or(Error::RaiseTerm("Failed to allocate binary"))?;
    binary.as_mut_slice().copy_from_slice(&cleaned);
    Ok(Binary::from_owned(binary, env))
}

/// Elixir remove null bytes
#[rustler::nif]
pub fn remove_null_bytes_nif<'a>(env: Env<'a>, input: Binary) -> Result<Binary<'a>, Error> {
    remove_null_bytes(env, input)
}


/// Remove control characters except tab, newline, carriage return, and other problematic characters
fn sanitize_csv_binary<'a>(env: Env<'a>, input: Binary) -> Result<Binary<'a>, Error> {
    let cleaned = sanitize_bytes(input.as_slice());
    let mut binary = OwnedBinary::new(cleaned.len())
        .ok_or(Error::RaiseTerm("Failed to allocate binary"))?;
    binary.as_mut_slice().copy_from_slice(&cleaned);
    Ok(Binary::from_owned(binary, env))
}

/// Elixir remove control characters except tab, newline, carriage return, and problematic characters
#[rustler::nif]
pub fn sanitize_csv_binary_nif<'a>(env: Env<'a>, input: Binary) -> Result<Binary<'a>, Error> {
    sanitize_csv_binary(env, input)
}

/// Strip BOM from binary (UTF-8, UTF-16 LE/BE)
fn strip_bom_binary<'a>(env: Env<'a>, input: Binary) -> Binary<'a> {
    let bytes = strip_bom(input.as_slice());
    Binary::from_slice(env, bytes)
}

/// Elixir strip BOM from binary (UTF-8, UTF-16 LE/BE)
#[rustler::nif]
pub fn strip_bom_binary_nif<'a>(env: Env<'a>, input: Binary) -> Binary<'a> {
    strip_bom_binary(env, input)
}

// ----------------------------------------------------------------------------
// Binary Helpers
// ----------------------------------------------------------------------------
fn sanitize_bytes(bytes: &[u8]) -> Vec<u8> {
    bytes.iter().copied()
        .filter(|&b| matches!(b, 0x09 | 0x0A | 0x0D | 0x20..=0x7E) || b >= 0x80)
        .collect()
}

fn strip_bom(bytes: &[u8]) -> &[u8] {
    if bytes.starts_with(&[0xEF, 0xBB, 0xBF]) { &bytes[3..] }
    else if bytes.starts_with(&[0xFF, 0xFE]) || bytes.starts_with(&[0xFE, 0xFF]) { &bytes[2..] }
    else { bytes }
}

// Copy on write (COW) avoids unnecessary copy operations
fn normalize_line_endings_cow(input: &str) -> Cow<str> {
    if input.contains("\r") || input.contains("\n") {
        Cow::Owned(input.replace("\r\n", "\n").replace('\r', "\n").replace('\n', "\r\n"))
    } else {
        Cow::Borrowed(input)
    }
}

/// Detect encoding by BOM or null byte patterns
/// Notes:
/// - Do this before removing BOM
fn detect_encoding(input: Binary) -> String {
    let bytes = input.as_slice();
    if bytes.starts_with(&[0xEF, 0xBB, 0xBF]) {
        "utf8_with_bom".to_string()
    } else if bytes.starts_with(&[0xFF, 0xFE]) {
        "utf16_le".to_string()
    } else if bytes.starts_with(&[0xFE, 0xFF]) {
        "utf16_be".to_string()
    } else {
        let null_count = bytes.iter().filter(|&&b| b == 0).count();
        if null_count > bytes.len() / 4 {
            "likely_utf16".to_string()
        } else if bytes.iter().all(|&b| (b >= 0x20 && b <= 0x7E) || matches!(b, 0x09 | 0x0A | 0x0D) || b >= 0x80) {
            "utf8".to_string()
        } else {
            "unknown".to_string()
        }
    }
}

/// Elixir detect encoding by BOM or null byte patterns
#[rustler::nif]
pub fn detect_encoding_nif(input: Binary) -> String {
    detect_encoding(input)
}

// ----------------------------------------------------------------------------
// Tests
// ----------------------------------------------------------------------------
#[cfg(test)]
mod tests {
    use super::*;

    // [x] TODO: update tests to work with new binary functions
    // [] TODO: connect to elixir for functionality
    #[test]
    fn test_remove_null_bytes() {
        // Note: files should not have null bytes
        let input = b"abc\0def\0".as_slice();
        let cleaned = sanitize_bytes(input);
        assert_eq!(cleaned, b"abcdef");
    }

    #[test]
    fn test_strip_bom() {
        // Windows and other systems can add byte order marks (BOM) to denote encoding
        let utf8_bom = &[0xEF, 0xBB, 0xBF, b'a', b'b', b'c'];
        let stripped = strip_bom(utf8_bom);
        assert_eq!(stripped, b"abc");

        let no_bom = &[b'a', b'b', b'c'];
        let stripped2 = strip_bom(no_bom);
        assert_eq!(stripped2, b"abc");
    }

    #[test]
    fn test_normalize_line_endings() {
        // different systems use different line endings
        let input = "line1\rline2\nline3\r\nline4";
        let normalized = normalize_line_endings_cow(input);
        assert_eq!(&normalized, "line1\r\nline2\r\nline3\r\nline4");
    }

    #[test]
    fn test_sanitize_csv_binary() {
        let input = b"abc\x00\x01def\t\n\r".as_slice();
        let cleaned = sanitize_bytes(input);
        assert_eq!(cleaned, b"abcdef\t\n\r");
    }

    #[test]
    fn test_check_csv_injection() {
        let eq = b"=SUM(A1:A2)";
        assert!(check_csv_injection(Binary::from_slice(rustler::Env::new(), eq)));
    }

    // #[test]
    // fn test_remove_null_bytes() {
    //     assert_eq!(remove_null_bytes("hi\0, no \0nulls".to_string()), "hi, no nulls");
    //     assert_eq!(remove_null_bytes("never had nulls".to_string()), "never had nulls");
    // }

    // #[test]
    // fn test_keep_normal_ascii_characters() {
    //     // This should now keep all characters expected.
    //     let input = "This is a test. Normal ASCII.";
    //     let output = sanitize_csv_string(input.to_string());
    //     assert_eq!(output, "This is a test. Normal ASCII.");
    // }

    // #[test]
    // fn test_remove_control_characters_except_tab_newline_cr() {
    //     let input = "Hi\x00\tThere\n\x07CR\r";
    //     let output = sanitize_csv_string(input.to_string());
    //     assert_eq!(output, "Hi\tThere\nCR\r");
    // }

    // #[test]
    // fn test_keep_utf8_characters() {
    //     let input = "Café 漢字 Привет"; // Should not be removed
    //     let output = sanitize_csv_string(input.to_string());
    // }

    // #[test]
    // fn removes_del_character() {
    //     let input = format!("Hello{}World", 0x7Fu8 as char);
    //     let output = sanitize_csv_string(input);
    //     assert_eq!(output, "HelloWorld");
    // }

    // #[test]
    // fn keeps_tabs_newlines_and_carriage_returns() {
    //     let input = "a\tb\nc\rd";
    //     let output = sanitize_csv_string(input.to_string());
    //     assert_eq!(output, "a\tb\nc\rd");
    // }

    // #[test]
    // fn removes_all_other_controls() {
    //     // Control Char Ranges = 0x01–0x08, 0x0B–0x0C, 0x0E–0x1F
    //     let bad_chars: String = (1u8..=31)
    //         .filter(|&b| !matches!(b, b'\t' | b'\n' | b'\r'))
    //         .map(|b| b as char)
    //         .collect();
    //     let input = format!("Good{}Bad", bad_chars);
    //     let output = sanitize_csv_string(input);
    //     assert_eq!(output, "GoodBad");
    // }
}


rustler::init!("Elixir.Orchestrate");
