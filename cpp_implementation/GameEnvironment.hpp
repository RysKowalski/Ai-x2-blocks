#include <array>
#include <cstdint>
#include <utility>

#pragma once

#define Obs std::array<int32_t, 37>
struct Info {
  int *game_level;
  int *move_count;
};
struct StepInfo {
  Obs *obs;
  double reward;
  bool terminated;
  bool truncated;
  Info info;
};

class GameEnv {
private:
  Obs state;
  int game_level;
  int move_count;
  std::array<bool, 5> available_moves;
  std::array<int32_t, 35> map_merges;
  int last_move_column;
  double reward;

  Obs *get_obs();
  Info get_info();
  void new_next();
  void fall_move_loop();
  void fall();
  bool merge();
  void merge_single(int i);
  void check_game_level();
  bool detect_termination();

public:
  GameEnv();
  std::pair<Obs *, Info> reset();
  StepInfo step(int action);
};
