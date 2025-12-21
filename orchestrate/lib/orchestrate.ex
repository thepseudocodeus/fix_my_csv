defmodule Orchestrate do
  @moduledoc """
  CSV data cleaning and normalization via Rust NIFs.
  """

  use Rustler,
    otp_app: :orchestrate,
    crate: "nif_actions",
    path: "../execute/nif_actions",
    mode: (if Mix.env() == :prod, do: :release, else: :debug)


  # --- NIF Functions ---

  @doc false
  def repair_and_normalize(_binary), do: :erlang.nif_error(:nif_not_loaded)

  @doc """
  Cleans and normalizes a CSV binary.
  """
  @spec clean_csv(binary()) :: binary()
  def clean_csv(binary) when is_binary(binary) do
    repair_and_normalize(binary)
  end

  @doc """
  Cleans a CSV file and writes to new file.

  ## Parameters

    - `input_path` - Path to potentially corrupted CSV file
    - `output_path` - Path cleaned CSV

  ## Returns

  `{:ok, stats}` tuple with cleaning statistics, or `{:error, reason}`.

  ## Examples

      Orchestrate.clean_csv_file("dirty.csv")
      # Creates dirty_cleaned.csv

      Orchestrate.clean_csv_file("dirty.csv", "clean.csv")
      # Creates clean.csv

  """
  @spec clean_csv_file(Path.t(), Path.t() | nil) :: {:ok, map()} | {:error, term()}
  def clean_csv_file(input_path, output_path \\ nil) do
    output_path = output_path || default_output_path(input_path)

    with {:ok, dirty_data} <- File.read(input_path),
         cleaned_data <- clean_csv(dirty_data),
         :ok <- File.write(output_path, cleaned_data) do
      {:ok, %{
        input: input_path,
        output: output_path,
        original_size: byte_size(dirty_data),
        cleaned_size: byte_size(cleaned_data),
        bytes_removed: byte_size(dirty_data) - byte_size(cleaned_data)
      }}
    else
      {:error, reason} -> {:error, reason}
    end
  end

  @doc """
  Removes null bytes.
  """
  @spec remove_null_bytes_nil(binary()) :: binary()
  def remove_null_bytes_nil(input) when is_binary(input) do
    clean_csv(input)
  end

  defp default_output_path(input_path) do
    input_path
    |> Path.rootname()
    |> Kernel.<>("_cleaned")
    |> Kernel.<>(Path.extname(input_path))
  end
end
