#include "GameEnvironment.hpp"
#include <algorithm>
#include <cstddef>
#include <cstdint>
#include <cstdlib>
#include <iostream>

GameEnv::GameEnv() {
  state = {};
  game_level = 0;
  move_count = 0;
  available_moves = {};

  map_merges = {};
  last_move_column = 0;
  reward = 0;
}

std::array<int32_t, 37> *GameEnv::get_obs() { return &state; }

Info GameEnv::get_info() { return {&game_level, &move_count}; }

std::pair<Obs *, Info> GameEnv::reset() {
  state = {};
  new_next();
  new_next();
  game_level = 0;
  move_count = 0;
  available_moves = {true, true, true, true, true};

  return {get_obs(), get_info()};
}

StepInfo GameEnv::step(int action) {
  last_move_column = action;
  reward = 0;

  int i = action * 7 + 6;
  bool canMergeOnTop = state[i] == state[35] + 1;
  if (state[i] == 0 or canMergeOnTop) {
    move_count += 1;
    reward += 0.01;

    if (canMergeOnTop)
      state[i] = state[35] + 1;
    else
      state[i] = state[35];
    new_next();

    fall_move_loop();
  } else {
    reward -= 0.1;
  }

  bool truncated = false;
  bool terminated = detect_termination();
  for (int i = 0; i < 5; i++) {
    if (not available_moves[i])
      reward -= 0.2;
  }

  return {get_obs(), reward, terminated, truncated, get_info()};
}

void GameEnv::new_next() {
  state[35] = state[36];
  state[36] = rand() % 7;
}

void GameEnv::fall_move_loop() {
  bool merged = true;
  std::cout << "\nfall_move_loop\n\n";
  while (merged) {
    fall();
    merged = merge();
  }
}

void GameEnv::fall() {
  for (std::size_t col = 0; col < 5; col++) {
    const std::size_t start = col * 7;
    std::size_t write = start;

    for (std::size_t row = start; row < start + 7; row++) {
      if (state[row] != 0) {
        state[write] = state[row];
        write++;
      }
    }

    while (write < start + 7) {
      state[write] = 0;
      write++;
    }
  }
}

bool GameEnv::merge() {
  std::cout << "\nmerge1\n\n";
  for (int col = 0; col < 5; col++) {
    for (int row = 0; row < 7; row++) {
      int i = col * 7 + row;
      int32_t *cell = &state[i];
      std::cout << "\n" << i << " " << *cell << "\n";

      if (*cell == 0) {
        map_merges[i] = 0;
        continue;
      }
      int same_tiles = 0;

      if (col > 0)
        if (state[i - 7] == *cell)
          same_tiles++;
      if (col < 4)
        if (state[i + 7] == *cell)
          same_tiles++;
      if (row > 0)
        if (state[i - 1] == *cell)
          same_tiles++;
      if (row < 6)
        if (state[i + 1] == *cell)
          same_tiles++;
    }
  }

  int best_pos = -1;
  int best_score = -1;

  for (int col = 0; col < 5; col++) {
    for (int row = 0; row < 7; row++) {
      int i = col * 7 + row;

      int score = map_merges[i];

      if (score > best_score) {
        best_score = score;
        best_pos = i;
      } else if (score == best_score and best_pos != -1 and
                 col == last_move_column and best_pos / 7 != last_move_column)
        best_pos = i;
    }
  }

  if (best_score > 0 and best_pos != -1) {
    merge_single(best_pos);
    check_game_level();
    std::cout << "\nmerge2true\n\n";
    return true;
  }

  std::cout << "\nmerge2false " << best_score << " " << best_pos << "\n\n";
  return false;
}

void GameEnv::merge_single(int i) {
  int *c = &state[i];
  int static col = i / 7;
  int static row = i % 7;

  int amount = 0;
  if (col > 0)
    if (state[i - 7] == *c) {
      amount++;
      state[i - 7] = 0;
    }
  if (col < 4)
    if (state[i + 7] == *c) {
      amount++;
      state[i + 7] = 0;
    }
  if (row > 0)
    if (state[i - 1 == *c]) {
      amount++;
      state[i + 1] = 0;
    }
  if (row < 6)
    if (state[i + 1] == *c) {
      amount++;
      state[i - 1] = 0;
    }
  c += amount;
  reward += amount / 10.0;
}

void GameEnv::check_game_level() {
  int diff = *std::max_element(state.begin(), state.begin() + 35) - 11;

  if (diff > 0) {
    for (int i = 0; i < 35; i++) {
      state[i] = std::max(state[i], 0);
    }
    game_level += diff;
    reward += diff;
  }
}

bool GameEnv::detect_termination() {
  for (int i = 0; i < 5; i++)
    available_moves[i] = state[i * 7 + 6] == state[36];
  return not std::none_of(available_moves.begin(), available_moves.end(),
                          [](bool move) { return move; });
}
