use std::error::Error;
use std::fs::File;
use std::io::BufReader;
use std::env;

fn main() {
    let base_path = "test_csvs/test_1.csv";
    // let current_dir = env::current_dir();
    let current_dir = env::current_dir().expect("Failed to get current directory");
    println!("Current working directory: {}", current_dir.display());
    // let test_file = format!("{}/{}", &current_dir.expect("REASON").display(), base_path);
    let test_file = current_dir.join(base_path);
    println!("Full path: {}", test_file.display());
    // println!("File Locations: {test_file}");
    // let result = validate_with_csv(test_file);
    // println!("Result: {result:?}");
    if let Err(err) = validate_with_csv(test_file.to_str().unwrap()) {
        eprintln!("Validation Error: {err}");
    }
}

// Approach #1: Use CSV to validate
// Notes:
// - https://docs.rs/csv/1.1.6/csv/
// - Ensure csv crate is installed
fn validate_with_csv(file_path: &str) -> Result<(), Box<dyn Error>> {
    let f = File::open(file_path)?;
    let mut rdr = csv::Reader::from_reader(BufReader::new(f));

    for result in rdr.records() {
        let record = result?;
        println!("{:?}", record);

    }
    println!("File is valid.");
    Ok(())
}
