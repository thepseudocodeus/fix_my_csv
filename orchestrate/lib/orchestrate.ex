defmodule Orchestrate do
  @moduledoc """
  Documentation for `Orchestrate`.
  """

  @doc """

  ## Examples

      iex> Orchestrate.remove_null_bytes_nil("hi\0 y'all")
      "hi y'all"

  """
  use Rustler,
    otp_app: :orchestrate,
    crate: "nif_actions",
    path: "../execute/nif_actions",
    mode: (if Mix.env() == :prod, do: :release, else: :debug)

  # Calls function from rust
  def init_context(_input), do: :erlang.nif_error(:nif_not_loaded)
  def repair_and_normalize(_resource), do: :erlang.nif_error(:nif_not_loaded)

  @doc """
  Call rust functions to repair csv files.
  """
  def clean_csv(binary) when is_binary(binary) do
    resource = init_context(binary)
    repair_and_normalize(resource)
  end

  @doc """
  Example usage for null byte removal testing.
  """
  def remove_null_bytes_nil(input) do
    clean_csv(input)
  end

  def hello, do: :world
end
