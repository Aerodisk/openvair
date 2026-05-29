"""Paths and module list for the linter vs LLM benchmark."""

from __future__ import annotations

from pathlib import Path

EXPERIMENT_ROOT = Path(__file__).resolve().parent
REPO_ROOT = EXPERIMENT_ROOT.parent

# Nine modules from the thesis protocol (README experiment).
MODULES: tuple[str, ...] = (
    'template',
    'storage',
    'backup',
    'event_store',
    'image',
    'network',
    'user',
    'virtual_machines',
    'volume',
)

TARGET_MUTATION_COUNT = 43

SPECS_SOURCE_DIR = REPO_ROOT / 'specs'
MUTATED_SPECS_DIR = EXPERIMENT_ROOT / 'mutated_specs'
GROUND_TRUTH_PATH = EXPERIMENT_ROOT / 'ground_truth.json'
RESULTS_DIR = EXPERIMENT_ROOT / 'results'

OPENVAIR_MODULES_DIR = REPO_ROOT / 'openvair' / 'modules'

# LLM defaults (override via experiment/.env)
DEFAULT_OPENAI_MODEL = 'gpt-5.5'
DEFAULT_REASONING_EFFORT = 'low'
# OpenAI Standard pricing for gpt-5.5 (USD per 1M tokens).
DEFAULT_LLM_INPUT_COST_PER_1M = 5.0
DEFAULT_LLM_CACHED_INPUT_COST_PER_1M = 0.5
DEFAULT_LLM_OUTPUT_COST_PER_1M = 30.0
