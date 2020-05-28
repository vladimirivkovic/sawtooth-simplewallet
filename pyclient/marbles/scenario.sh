#!/bin/bash

sawtooth keygen jack

marble init marble1 blue 35 tom
marble init marble2 red 50 tom
marble init marble3 blue 70 tom
marble init marble4 green 30 jerry
marble init marble7 green 20 jerry
marble init marble8 red 40 jerry
marble init marble9 blue 30 tom

marble read marble2
marble transfer marble2 jerry
marble init marble5 red 70 tom
marble init marble10 green 30 jerry
marble read marble1
marble transfer marble4 tom
# marble transferByColor blue jerry
marble init marble6 red 60 tom
marble read marble4

# marble transferByColor red spike
# marble transferByColor green spike
marble delete marble2
marble transfer marble4 tyke
marble delete marble4
marble transfer marble1 tyke
marble delete marble3
marble delete marble1
marble delete marble5
marble delete marble7
marble delete marble8
marble delete marble9