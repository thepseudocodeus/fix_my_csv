defmodule Mix.Tasks.CleanCsv do
  @moduledoc """
  Mix task to clean CSV files.

  ## Usage

      mix clean_csv file.csv
      mix clean_csv file.csv output.csv
      mix clean_csv *.csv --batch

  """
  use Mix.Task

  @shortdoc "Cleans CSV files by removing null bytes and normalizing line endings"

  @impl Mix.Task
  def run(args) do
    Mix.Task.run("app.start")

    case args do
      ["--help"] ->
        print_help()

      ["--batch" | patterns] ->
        batch_clean(patterns)

      [input] ->
        clean_single(input, nil)

      [input, output] ->
        clean_single(input, output)

      _ ->
        Mix.shell().error("Invalid arguments. Use --help for usage.")
    end
  end

  defp clean_single(input, output) do
    case Orchestrate.clean_csv_file(input, output) do
      {:ok, stats} ->
        Mix.shell().info("✅ Cleaned: #{stats.output}")
        Mix.shell().info("   Removed #{stats.bytes_removed} bytes")

      {:error, reason} ->
        Mix.shell().error("❌ Error: #{inspect(reason)}")
    end
  end

  defp batch_clean(patterns) do
    patterns = if Enum.empty?(patterns), do: ["*.csv"], else: patterns

    files =
      patterns
      |> Enum.flat_map(&Path.wildcard/1)
      |> Enum.reject(&String.ends_with?(&1, "_cleaned.csv"))
      |> Enum.uniq()

    Mix.shell().info("🔍 Found #{length(files)} files\n")

    Enum.each(files, fn file ->
      Mix.shell().info("Processing: #{file}")
      clean_single(file, nil)
    end)
  end

  defp print_help do
    Mix.shell().info("""
    Usage:
      mix clean_csv <input_file> [output_file]
      mix clean_csv --batch [pattern...]

    Examples:
      mix clean_csv dirty.csv
      mix clean_csv dirty.csv clean.csv
      mix clean_csv --batch *.csv
      mix clean_csv --batch data/*.csv reports/*.csv
    """)
  end
end
