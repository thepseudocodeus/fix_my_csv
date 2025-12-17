defmodule OrchestrateTest do
  use ExUnit.Case
  doctest Orchestrate

  test "greets the world" do
    assert Orchestrate.hello() == :world
  end
end
