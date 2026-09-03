#pragma once

#include <array>
#include <cstddef>

class Game {
public:
  Game(const std::size_t width, const std::size_t height);
  ~Game();
  std::array<int, 5> actions;
  void move(int move);
  double reward;

private:
  std::array<std::array<typename int, 7>, 5>
};
