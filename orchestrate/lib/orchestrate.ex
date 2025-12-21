defmodule Orchestrate do
  @moduledoc """
  CSV data cleaning and normalization via Rust NIFs.

  Orchestrate uses Rust NIF functions to clean and normalize CSV data.

  1. Binary
  - Encoding conversion (any encoding → UTF-8)
  - Line ending normalization (CRLF, CR → LF)
  - Null byte removal
  - Control character sanitization

  2. Data
  - Strip spaces
  - Reduce multiple spaces to a single space
  - Reduce multiple newlines to a single newline
  - Remove leading and trailing newlines
  - Ensure comma is the delimiter

  3. Structure
  - Limit file size
  - Limit number of rows
  - Return CSV than and parquet

  ## Examples

      iex> Orchestrate.clean_csv("id,name\\r\\n1,test\\r\\n")
      "id,name\\n1,test\\n"

      iex> Orchestrate.clean_csv("hello\\0world")
      "helloworld"

      iex> Orchestrate.remove_null_bytes_nil("hi\\0 y'all")
      "hi y'all"

  """

  use Rustler,
    otp_app: :orchestrate,
    crate: "nif_actions",
    path: "../execute/nif_actions",
    mode: if(Mix.env() == :prod, do: :release, else: :debug)

  @doc false
  def repair_and_normalize(_binary), do: :erlang.nif_error(:nif_not_loaded)

  # --- Public API ---

  @doc """
  Cleans and normalizes a CSV binary.

  Performs the following transformations:
  1. Detects and converts source encoding to UTF-8
  2. Normalizes all line endings to Unix-style (\\n)
  3. Removes null bytes (\\0)
  4. Strips control characters (preserves \\n and \\t)

  ## Parameters

    - `binary` - The CSV data as a binary string

  ## Returns

  A cleaned binary string ready for CSV parsing.

  ## Examples

      iex> Orchestrate.clean_csv("id,name\\r\\n1,test")
      "id,name\\n1,test"

      iex> Orchestrate.clean_csv("col1\\tcol2\\n")
      "col1\\tcol2\\n"

  """
  @spec clean_csv(binary()) :: binary()
  def clean_csv(binary) when is_binary(binary) do
    repair_and_normalize(binary)
  end

  @doc """
  Removes null bytes from input string.

  ## Examples

      iex> Orchestrate.remove_null_bytes_nil("hi\\0 y'all")
      "hi y'all"

  """
  @spec remove_null_bytes_nil(binary()) :: binary()
  def remove_null_bytes_nil(input) when is_binary(input) do
    clean_csv(input)
  end
end
