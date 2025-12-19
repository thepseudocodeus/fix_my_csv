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
  def remove_null_bytes_nif(_input), do: :erlang.nif_error(:nif_not_loaded)

  def hello do
    :world
  end
end
