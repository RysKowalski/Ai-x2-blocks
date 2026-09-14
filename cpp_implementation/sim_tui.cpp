#include "sim_tui.hpp"
#include "GameEnvironment.hpp"

#include <array>
#include <iomanip>
#include <iostream>
#include <string>

namespace {

constexpr int MAP_WIDTH = 5;
constexpr int MAP_HEIGHT = 7;
constexpr int MAP_SIZE = MAP_WIDTH * MAP_HEIGHT;

void clear_screen() { // std::cout << "\033[2J\033[H";//
}

void print_state(const Obs &obs, double reward) {
  std::cout << "┌";

  for (int i = 0; i < MAP_WIDTH * 4 - 1; ++i) {
    std::cout << "─";
  }

  std::cout << "┐\n";

  for (int row = MAP_HEIGHT - 1; row >= 0; --row) {
    std::cout << "│";

    for (int column = 0; column < MAP_WIDTH; ++column) {
      const int index = column * MAP_HEIGHT + row;
      const int value = obs[index];

      std::cout << " " << std::setw(2) << value << "│";
    }

    std::cout << '\n';
  }

  std::cout << "└";

  for (int i = 0; i < MAP_WIDTH * 4 - 1; ++i) {
    std::cout << "─";
  }

  std::cout << "┘\n";

  std::cout << "Next: [" << obs[MAP_SIZE] << ", " << obs[MAP_SIZE + 1]
            << "], reward: " << std::fixed << std::setprecision(4) << reward
            << '\n';
}

void print_finished_state(const Obs &obs, double reward, const Info &info) {
  clear_screen();

  std::cout << "Map:\n";

  for (int row = MAP_HEIGHT - 1; row >= 0; --row) {
    for (int column = 0; column < MAP_WIDTH; ++column) {
      const int index = column * MAP_HEIGHT + row;

      std::cout << std::setw(3) << obs[index];

      if (column + 1 < MAP_WIDTH) {
        std::cout << ' ';
      }
    }

    std::cout << '\n';
  }

  std::cout << '\n';

  std::cout << "Next: [" << obs[MAP_SIZE] << ", " << obs[MAP_SIZE + 1] << "]\n";

  std::cout << '\n';

  std::cout << "Reward: " << reward << '\n';

  std::cout << "Info: game_level=";

  if (info.game_level != nullptr) {
    std::cout << *info.game_level;
  } else {
    std::cout << "null";
  }

  std::cout << ", move_count=";

  if (info.move_count != nullptr) {
    std::cout << *info.move_count;
  } else {
    std::cout << "null";
  }

  std::cout << '\n';
  std::cout << '\n';
  std::cout << "Episode finished.\n";
}

void run_tui(GameEnv &env) {
  const auto [reset_obs, reset_info] = env.reset();

  (void)reset_info;

  bool terminated = false;
  bool truncated = false;

  while (true) {
    if (reset_obs != nullptr && !terminated && !truncated) {
      print_state(*reset_obs, 0.0);
    }

    std::cout << '\n';
    std::cout << "Choose action [1-5], or q to quit:\n";
    std::cout << "> " << std::flush;

    std::string command;

    if (!std::getline(std::cin, command)) {
      break;
    }

    if (command == "q" || command == "Q") {
      break;
    }

    int action = 0;

    try {
      std::size_t position = 0;
      action = std::stoi(command, &position);

      if (position != command.size()) {
        throw std::invalid_argument("invalid action");
      }
    } catch (const std::exception &) {
      std::cout << "Invalid action.\n";
      std::cout << "Press Enter...";

      std::string ignored;
      std::getline(std::cin, ignored);
      continue;
    }

    if (action < 1 || action > 5) {
      std::cout << "Action must be between 1 and 5.\n";
      std::cout << "Press Enter...";

      std::string ignored;
      std::getline(std::cin, ignored);
      continue;
    }

    const StepInfo result = env.step(action - 1);

    terminated = result.terminated;
    truncated = result.truncated;

    if (result.obs != nullptr && !terminated && !truncated) {
      clear_screen();
      print_state(*result.obs, result.reward);
      continue;
    }

    if (terminated || truncated) {
      if (result.obs != nullptr) {
        print_finished_state(*result.obs, result.reward, result.info);
      }

      std::cout << "Press Enter to reset...";

      std::string ignored;
      std::getline(std::cin, ignored);

      const auto [obs, info] = env.reset();

      (void)info;

      terminated = false;
      truncated = false;

      if (obs != nullptr) {
        clear_screen();
        print_state(*obs, 0.0);
      }
    }
  }
}

} // namespace

void tui() {
  GameEnv env;
  run_tui(env);
}
