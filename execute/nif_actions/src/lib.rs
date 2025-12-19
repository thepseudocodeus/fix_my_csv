use rustler::NifResult;


fn remove_null_bytes(input: String) -> String {
    // Replaces null bytes with empty string
    // Notes:
    // - To test, moved core functionality into this private function
    input.replace("\0", "")
}

#[rustler::nif]
pub fn remove_null_bytes_nif(input: String) -> String {
    remove_null_bytes(input)
}


#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_remove_null_bytes() {
        assert_eq!(remove_null_bytes("hi\0, no \0nulls".to_string()), "hi, no nulls");
        assert_eq!(remove_null_bytes("never had nulls".to_string()), "never had nulls");
    }
}


rustler::init!("Elixir.Orchestrate");
