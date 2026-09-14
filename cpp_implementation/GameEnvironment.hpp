#include <array>
#include <cstdint>
#include <utility>
struct Obs {};
struct Info {};
struct StepInfo {};

class GameEnv {
private:
  std::array<int32_t, 37> state;
  int game_level;
  std::array<bool, 5> avalible_moves;

  std::array<int32_t, 35> map_merges;
  int last_move_column;
  double reward;

  Obs get_obs();
  Info get_info();
  void new_next();
  void fall_move_loop();
  void fall();
  bool merge();
  void merge_single();
  void check_game_level();
  bool detect_termination();

public:
  GameEnv();
  std::pair<Obs, Info> reset();
  StepInfo step(int action);
};
