cmake_minimum_required(VERSION 3.23)

project(Ai-x2-blocks)

add_executable(main)
target_sources(main
  PRIVATE
    main.cpp
    GameEnvironment.cpp
    sim_tui.cpp
)
