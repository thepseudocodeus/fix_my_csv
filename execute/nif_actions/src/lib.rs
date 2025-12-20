use rustler::NifResult;

/// Removes null bytes
fn remove_null_bytes(input: String) -> String {
    // Replaces null bytes with empty string
    // Notes:
    // - To test, moved core functionality into this private function
    input.replace("\0", "")
}

#[rustler::nif]
pub fn remove_null_bytes_nif(input: String) -> String {
    remove_null_bytes(&input)
}

/// Remove control characters but retain tab, newline, and carriage returns
/// Note: Windows and legacy MacOs can use unsupported characters
fn sanitize_csv_string(input: String) -> String {
    // Iterate through characters
    input.chars()
        .filter(|&c| {
            matches!(c, '\t' | '\n' | '\r') ||
            (c >= ' ' && c <= '~') ||
            c as u32 >= 0x80 // [] TODO: Add rust documentation section on why this is needed for UTF-8
        })
        .collect()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_remove_null_bytes() {
        assert_eq!(remove_null_bytes("hi\0, no \0nulls".to_string()), "hi, no nulls");
        assert_eq!(remove_null_bytes("never had nulls".to_string()), "never had nulls");
    }

    #[test]
    fn test_keep_normal_ascii_characters() {
        // This should now keep all characters expected.
        let input = "This is a test. Normal ASCII.";
        let output = sanitize_csv_string(input.to_string());
        assert_eq!(output, "This is a test. Normal ASCII.");
    }

    #[test]
    fn test_remove_control_characters_except_tab_newline_cr() {
        let input = "Hi\x00\tThere\n\x07CR\r";
        let output = sanitize_csv_string(input.to_string());
        assert_eq!(output, "Hi\tThere\nCR\r");
    }

    #[test]
    fn test_keep_utf8_characters() {
        let input = "Café 漢字 Привет"; // Should not be removed
        let output = sanitize_csv_string(input.to_string());
    }
}


rustler::init!("Elixir.Orchestrate");
