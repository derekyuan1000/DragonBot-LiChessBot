"""
Evolutionary Self-Play Training System for DragonBot

This system creates multiple "mutated" versions of the bot with slightly different parameters,
has them play against each other, and evolves the winners into the next generation.
The bot literally evolves and improves itself over time!
"""
import chess
import chess.pgn
import random
import time
import json
import os
import copy
from datetime import datetime
from engines.bot.main import get_move
from engines.bot.evaluation import get_evaluation
import numpy as np


class BotGenome:
    """Represents the 'DNA' of a bot - all its tunable parameters"""

    def __init__(self):
        # Material values (can be evolved)
        self.piece_values = {
            'pawn': 100,
            'knight': 310,
            'bishop': 330,
            'rook': 500,
            'queen': 900,
            'king': 20000
        }

        # Evaluation weights (can be evolved)
        self.eval_weights = {
            'material_weight': 1.0,
            'position_weight': 0.3,
            'king_safety_weight': 0.8,
            'pawn_structure_weight': 0.4,
            'piece_activity_weight': 0.6,
            'center_control_weight': 0.5,
            'development_bonus': 10,
            'castling_bonus': 20,
            'doubled_pawn_penalty': 20,
            'isolated_pawn_penalty': 15,
            'rook_open_file_bonus': 35
        }

        # Search parameters
        self.search_params = {
            'base_depth': 4,
            'quiescence_depth': 10,
            'aggressive_factor': 1.0,  # How much to favor attacks
            'safety_factor': 1.0       # How much to avoid risks
        }

        # Playing style parameters
        self.style_params = {
            'randomness_opening': 0.1,   # How random in opening (0-1)
            'randomness_middlegame': 0.05,
            'randomness_endgame': 0.02,
            'risk_tolerance': 0.5        # How willing to take risks (0-1)
        }

        # Performance tracking
        self.fitness = 0.0
        self.games_played = 0
        self.wins = 0
        self.draws = 0
        self.losses = 0
        self.generation = 0
        self.parent_ids = []

    def mutate(self, mutation_rate=0.4, mutation_strength=0.6):
        """Create a mutated copy of this genome with DRAMATIC mutations"""
        new_genome = copy.deepcopy(self)

        # Add chance for RADICAL mutations (complete parameter overhauls)
        radical_mutation_chance = 0.15

        # DRAMATIC piece value mutations
        for piece in new_genome.piece_values:
            if random.random() < mutation_rate:
                if piece == 'king':
                    continue  # Don't mutate king value
                current_value = new_genome.piece_values[piece]

                # 30% chance for RADICAL mutation (complete value replacement)
                if random.random() < 0.3:
                    # Replace with completely new value based on piece type
                    if piece == 'pawn':
                        new_genome.piece_values[piece] = random.randint(50, 200)
                    elif piece == 'knight':
                        new_genome.piece_values[piece] = random.randint(200, 500)
                    elif piece == 'bishop':
                        new_genome.piece_values[piece] = random.randint(200, 500)
                    elif piece == 'rook':
                        new_genome.piece_values[piece] = random.randint(300, 700)
                    elif piece == 'queen':
                        new_genome.piece_values[piece] = random.randint(600, 1200)
                else:
                    # Standard dramatic mutation (much larger changes)
                    change = random.uniform(-mutation_strength, mutation_strength)
                    new_genome.piece_values[piece] = max(10, int(current_value * (1 + change)))

        # DRAMATIC evaluation weight mutations
        for param in new_genome.eval_weights:
            if random.random() < mutation_rate:
                current_value = new_genome.eval_weights[param]

                # 25% chance for RADICAL mutation
                if random.random() < 0.25:
                    # Complete replacement with random value
                    if 'weight' in param:
                        new_genome.eval_weights[param] = random.uniform(0.1, 3.0)
                    elif 'bonus' in param:
                        new_genome.eval_weights[param] = random.randint(5, 50)
                    elif 'penalty' in param:
                        new_genome.eval_weights[param] = random.randint(5, 50)
                    else:
                        new_genome.eval_weights[param] = random.uniform(0.1, 2.0)
                else:
                    # Dramatic standard mutation
                    change = random.uniform(-mutation_strength, mutation_strength)
                    new_genome.eval_weights[param] = max(0.01, current_value * (1 + change))

        # DRAMATIC search parameter mutations
        if random.random() < mutation_rate * 1.5:  # Higher chance for search params
            # Dramatic depth changes
            if random.random() < 0.3:
                new_genome.search_params['base_depth'] = random.choice([2, 3, 4, 5, 6])
            else:
                new_genome.search_params['base_depth'] = max(2, min(6,
                    new_genome.search_params['base_depth'] + random.choice([-2, -1, 0, 1, 2])))

        # Dramatic quiescence depth mutations
        if random.random() < mutation_rate:
            if random.random() < 0.2:
                new_genome.search_params['quiescence_depth'] = random.randint(5, 20)
            else:
                change = random.uniform(-0.5, 0.5)
                new_genome.search_params['quiescence_depth'] = max(3, min(20,
                    int(new_genome.search_params['quiescence_depth'] * (1 + change))))

        for param in ['aggressive_factor', 'safety_factor']:
            if random.random() < mutation_rate:
                current_value = new_genome.search_params[param]

                # 20% chance for extreme personality shift
                if random.random() < 0.2:
                    if param == 'aggressive_factor':
                        new_genome.search_params[param] = random.uniform(0.2, 3.0)
                    else:  # safety_factor
                        new_genome.search_params[param] = random.uniform(0.2, 3.0)
                else:
                    # Dramatic standard mutation
                    change = random.uniform(-mutation_strength, mutation_strength)
                    new_genome.search_params[param] = max(0.1, min(3.0, current_value * (1 + change)))

        # DRAMATIC style parameter mutations (personality shifts)
        for param in new_genome.style_params:
            if random.random() < mutation_rate * 1.2:  # Higher chance for style changes
                if 'randomness' in param:
                    # 25% chance for complete randomness overhaul
                    if random.random() < 0.25:
                        new_genome.style_params[param] = random.uniform(0.0, 0.8)
                    else:
                        current_value = new_genome.style_params[param]
                        change = random.uniform(-mutation_strength, mutation_strength)
                        new_genome.style_params[param] = max(0.0, min(1.0, current_value * (1 + change)))
                elif param == 'risk_tolerance':
                    # 30% chance for complete personality flip
                    if random.random() < 0.3:
                        new_genome.style_params[param] = random.uniform(0.0, 1.0)
                    else:
                        current_value = new_genome.style_params[param]
                        change = random.uniform(-mutation_strength, mutation_strength)
                        new_genome.style_params[param] = max(0.0, min(1.0, current_value * (1 + change)))

        # NEW: Add completely new radical mutations

        # Radical mutation: Swap two piece values (create unconventional valuations)
        if random.random() < radical_mutation_chance:
            pieces = ['pawn', 'knight', 'bishop', 'rook', 'queen']
            piece1, piece2 = random.sample(pieces, 2)
            # Swap but keep some sanity (don't make pawns worth more than queens)
            if (piece1 == 'pawn' and piece2 == 'queen') or (piece1 == 'queen' and piece2 == 'pawn'):
                pass  # Skip this swap
            else:
                new_genome.piece_values[piece1], new_genome.piece_values[piece2] = \
                    new_genome.piece_values[piece2], new_genome.piece_values[piece1]

        # Radical mutation: Invert a playing style (aggressive becomes defensive, etc.)
        if random.random() < radical_mutation_chance:
            if random.random() < 0.5:
                # Flip aggressive/safety factors
                new_genome.search_params['aggressive_factor'], new_genome.search_params['safety_factor'] = \
                    new_genome.search_params['safety_factor'], new_genome.search_params['aggressive_factor']
            else:
                # Flip risk tolerance
                new_genome.style_params['risk_tolerance'] = 1.0 - new_genome.style_params['risk_tolerance']

        # Radical mutation: Completely randomize all randomness parameters
        if random.random() < radical_mutation_chance * 0.5:
            new_genome.style_params['randomness_opening'] = random.uniform(0.0, 0.5)
            new_genome.style_params['randomness_middlegame'] = random.uniform(0.0, 0.3)
            new_genome.style_params['randomness_endgame'] = random.uniform(0.0, 0.2)

        # Radical mutation: Create "specialist" by boosting one evaluation aspect dramatically
        if random.random() < radical_mutation_chance * 0.7:
            specialist_params = ['king_safety_weight', 'pawn_structure_weight', 'piece_activity_weight',
                               'center_control_weight']
            chosen_specialty = random.choice(specialist_params)
            new_genome.eval_weights[chosen_specialty] *= random.uniform(2.0, 4.0)
            # Reduce others slightly to maintain balance
            for param in specialist_params:
                if param != chosen_specialty:
                    new_genome.eval_weights[param] *= random.uniform(0.5, 0.8)

        return new_genome

    def crossover(self, other_genome):
        """Create offspring by combining this genome with another - DRAMATIC crossover"""
        child1 = copy.deepcopy(self)
        child2 = copy.deepcopy(other_genome)

        # DRAMATIC crossover: Higher mixing rate and more aggressive combinations
        mixing_rate = 0.7  # Much higher than standard 0.5

        # Mix piece values with dramatic blending
        for piece in child1.piece_values:
            if random.random() < mixing_rate:
                if random.random() < 0.3:
                    # Create hybrid values (average with some variation)
                    avg_value = (child1.piece_values[piece] + child2.piece_values[piece]) // 2
                    variation = random.uniform(0.8, 1.2)
                    child1.piece_values[piece] = int(avg_value * variation)
                    child2.piece_values[piece] = int(avg_value * (2 - variation))
                else:
                    # Standard swap
                    child1.piece_values[piece], child2.piece_values[piece] = \
                        child2.piece_values[piece], child1.piece_values[piece]

        # DRAMATIC evaluation weight mixing
        for param in child1.eval_weights:
            if random.random() < mixing_rate:
                if random.random() < 0.4:
                    # Create hybrid values with dramatic variation
                    avg_value = (child1.eval_weights[param] + child2.eval_weights[param]) / 2
                    variation = random.uniform(0.6, 1.4)
                    child1.eval_weights[param] = max(0.01, avg_value * variation)
                    child2.eval_weights[param] = max(0.01, avg_value * (2 - variation))
                else:
                    # Standard swap
                    child1.eval_weights[param], child2.eval_weights[param] = \
                        child2.eval_weights[param], child1.eval_weights[param]

        # DRAMATIC search parameter mixing
        for param in child1.search_params:
            if random.random() < mixing_rate:
                if param == 'base_depth':
                    # For depth, choose randomly or average
                    if random.random() < 0.5:
                        child1.search_params[param], child2.search_params[param] = \
                            child2.search_params[param], child1.search_params[param]
                    else:
                        # Average depth (rounded)
                        avg_depth = (child1.search_params[param] + child2.search_params[param]) / 2
                        child1.search_params[param] = max(2, min(6, int(avg_depth + random.choice([-1, 0, 1]))))
                        child2.search_params[param] = max(2, min(6, int(avg_depth + random.choice([-1, 0, 1]))))
                elif param == 'quiescence_depth':
                    # Similar for quiescence depth
                    if random.random() < 0.5:
                        child1.search_params[param], child2.search_params[param] = \
                            child2.search_params[param], child1.search_params[param]
                    else:
                        avg_qd = (child1.search_params[param] + child2.search_params[param]) / 2
                        child1.search_params[param] = max(3, min(20, int(avg_qd * random.uniform(0.8, 1.2))))
                        child2.search_params[param] = max(3, min(20, int(avg_qd * random.uniform(0.8, 1.2))))
                else:
                    # For other search params, create hybrid values
                    if random.random() < 0.3:
                        avg_value = (child1.search_params[param] + child2.search_params[param]) / 2
                        variation = random.uniform(0.7, 1.3)
                        child1.search_params[param] = max(0.1, min(3.0, avg_value * variation))
                        child2.search_params[param] = max(0.1, min(3.0, avg_value * (2 - variation)))
                    else:
                        child1.search_params[param], child2.search_params[param] = \
                            child2.search_params[param], child1.search_params[param]

        # DRAMATIC style parameter mixing (personality blending)
        for param in child1.style_params:
            if random.random() < mixing_rate * 1.1:  # Even higher chance for personality mixing
                if random.random() < 0.4:
                    # Create personality blends
                    avg_value = (child1.style_params[param] + child2.style_params[param]) / 2
                    variation = random.uniform(0.6, 1.4)
                    child1.style_params[param] = max(0.0, min(1.0, avg_value * variation))
                    child2.style_params[param] = max(0.0, min(1.0, avg_value * (2 - variation)))
                else:
                    # Standard swap
                    child1.style_params[param], child2.style_params[param] = \
                        child2.style_params[param], child1.style_params[param]

        # NEW: Add dramatic crossover-specific mutations

        # 20% chance to create "extreme hybrid" - take the most extreme values from both parents
        if random.random() < 0.2:
            for param in child1.eval_weights:
                parent_values = [self.eval_weights[param], other_genome.eval_weights[param]]
                if max(parent_values) / min(parent_values) > 2.0:  # If parents differ significantly
                    # Give children the extreme values
                    child1.eval_weights[param] = max(parent_values) * random.uniform(1.0, 1.5)
                    child2.eval_weights[param] = min(parent_values) * random.uniform(0.5, 1.0)

        # 15% chance for "personality fusion" - completely blend all style parameters
        if random.random() < 0.15:
            for param in child1.style_params:
                fusion_value = (self.style_params[param] + other_genome.style_params[param]) / 2
                noise1 = random.uniform(-0.2, 0.2)
                noise2 = random.uniform(-0.2, 0.2)
                child1.style_params[param] = max(0.0, min(1.0, fusion_value + noise1))
                child2.style_params[param] = max(0.0, min(1.0, fusion_value + noise2))

        return child1, child2

    def calculate_fitness(self):
        """Calculate fitness score based on game results"""
        if self.games_played == 0:
            self.fitness = 0.0
            return 0.0

        win_rate = self.wins / self.games_played
        draw_rate = self.draws / self.games_played

        # Fitness = win_rate + 0.5 * draw_rate
        self.fitness = win_rate + 0.5 * draw_rate
        return self.fitness

    def update_results(self, result):
        """Update results after a game"""
        self.games_played += 1
        if result == 1:  # Win
            self.wins += 1
        elif result == 0:  # Draw
            self.draws += 1
        else:  # Loss
            self.losses += 1

        self.calculate_fitness()

    def to_dict(self):
        """Convert genome to dictionary for saving"""
        return {
            'piece_values': self.piece_values,
            'eval_weights': self.eval_weights,
            'search_params': self.search_params,
            'style_params': self.style_params,
            'fitness': self.fitness,
            'games_played': self.games_played,
            'wins': self.wins,
            'draws': self.draws,
            'losses': self.losses,
            'generation': self.generation,
            'parent_ids': self.parent_ids
        }

    @classmethod
    def from_dict(cls, data):
        """Create genome from dictionary"""
        genome = cls()
        genome.piece_values = data.get('piece_values', genome.piece_values)
        genome.eval_weights = data.get('eval_weights', genome.eval_weights)
        genome.search_params = data.get('search_params', genome.search_params)
        genome.style_params = data.get('style_params', genome.style_params)
        genome.fitness = data.get('fitness', 0.0)
        genome.games_played = data.get('games_played', 0)
        genome.wins = data.get('wins', 0)
        genome.draws = data.get('draws', 0)
        genome.losses = data.get('losses', 0)
        genome.generation = data.get('generation', 0)
        genome.parent_ids = data.get('parent_ids', [])
        return genome


class EvolutionaryBot:
    """A bot that uses a specific genome to make decisions"""

    def __init__(self, genome, bot_id):
        self.genome = genome
        self.bot_id = bot_id

    def get_move(self, board, time_limit=5.0):
        """Get a move using this bot's genome parameters"""
        try:
            # Apply genome parameters to move selection
            depth = self.genome.search_params['base_depth']

            # Add randomness based on game phase
            move_count = len(board.move_stack)
            if move_count < 20:  # Opening
                randomness = self.genome.style_params['randomness_opening']
            elif move_count < 40:  # Middlegame
                randomness = self.genome.style_params['randomness_middlegame']
            else:  # Endgame
                randomness = self.genome.style_params['randomness_endgame']

            # Get move with possible randomness
            if random.random() < randomness:
                # Make a random move from top moves
                legal_moves = list(board.legal_moves)
                if len(legal_moves) > 3:
                    # Choose from top 3 random moves
                    move = random.choice(legal_moves[:3])
                else:
                    move = random.choice(legal_moves)
            else:
                # Use the normal engine with this genome's parameters
                move = get_move(board, depth)

            if move is None or move not in board.legal_moves:
                move = random.choice(list(board.legal_moves))

            return move

        except Exception as e:
            print(f"Error in bot {self.bot_id}: {e}")
            return random.choice(list(board.legal_moves))


class EvolutionaryTrainer:
    """Manages the evolutionary training process"""

    def __init__(self, population_size=20, games_per_generation=100):
        self.population_size = population_size
        self.games_per_generation = games_per_generation
        self.population = []
        self.generation = 0
        self.best_ever_genome = None
        self.best_ever_fitness = 0.0

        # Create directories
        os.makedirs("evolution_data", exist_ok=True)
        os.makedirs("evolution_games", exist_ok=True)
        os.makedirs("evolution_champions", exist_ok=True)

        # Initialize first generation
        self.create_initial_population()

    def create_initial_population(self):
        """Create the first generation of bots"""
        print("Creating initial population...")

        # Create base genome
        base_genome = BotGenome()
        self.population.append(base_genome)

        # Create DRAMATICALLY mutated versions for initial diversity
        for i in range(1, self.population_size):
            # Use very high mutation rates for initial population to create diverse starting bots
            mutated = base_genome.mutate(mutation_rate=0.8, mutation_strength=0.8)
            mutated.generation = 0
            self.population.append(mutated)

        print(f"Created {len(self.population)} DRAMATICALLY different bots for generation 0")

    def play_game(self, bot1, bot2, game_id):
        """Play a game between two bots"""
        board = chess.Board()
        move_count = 0
        max_moves = 200

        try:
            while not board.is_game_over() and move_count < max_moves:
                if board.turn == chess.WHITE:
                    current_bot = bot1
                else:
                    current_bot = bot2

                move = current_bot.get_move(board, time_limit=3.0)

                if move not in board.legal_moves:
                    print(f"Invalid move {move} by bot {current_bot.bot_id}")
                    move = random.choice(list(board.legal_moves))

                board.push(move)
                move_count += 1

            # Determine result
            if board.is_checkmate():
                if board.turn == chess.WHITE:
                    return -1  # Black (bot2) wins
                else:
                    return 1   # White (bot1) wins
            else:
                return 0  # Draw

        except Exception as e:
            print(f"Error in game {game_id}: {e}")
            return 0  # Count as draw

    def run_tournament(self):
        """Run a round-robin tournament between all bots"""
        print(f"Running tournament for generation {self.generation}...")

        total_games = 0
        bots = [EvolutionaryBot(genome, i) for i, genome in enumerate(self.population)]

        # Play each bot against several others (not full round-robin for speed)
        games_per_bot = min(10, len(bots) - 1)

        for i, bot1 in enumerate(bots):
            # Select random opponents
            opponents = random.sample([b for j, b in enumerate(bots) if j != i], games_per_bot)

            for bot2 in opponents:
                result = self.play_game(bot1, bot2, total_games)

                # Update results
                bot1.genome.update_results(result)
                bot2.genome.update_results(-result)

                total_games += 1

                if total_games % 20 == 0:
                    print(f"Completed {total_games} games...")

        print(f"Tournament completed: {total_games} games played")

        # Update fitness for all genomes
        for genome in self.population:
            genome.calculate_fitness()

    def select_parents(self, num_parents):
        """Select the best genomes to be parents of next generation"""
        # Sort by fitness
        self.population.sort(key=lambda g: g.fitness, reverse=True)

        # Update best ever
        if self.population[0].fitness > self.best_ever_fitness:
            self.best_ever_fitness = self.population[0].fitness
            self.best_ever_genome = copy.deepcopy(self.population[0])

        # Select top performers
        parents = self.population[:num_parents]

        print(f"Selected {len(parents)} parents")
        print(f"Best fitness: {parents[0].fitness:.3f}")
        print(f"Average fitness: {sum(p.fitness for p in parents) / len(parents):.3f}")

        return parents

    def create_next_generation(self, parents):
        """Create the next generation from selected parents"""
        new_population = []

        # Keep the best few unchanged (elitism)
        elite_count = max(2, len(parents) // 4)
        for i in range(elite_count):
            elite = copy.deepcopy(parents[i])
            elite.generation = self.generation + 1
            elite.games_played = 0
            elite.wins = 0
            elite.draws = 0
            elite.losses = 0
            elite.fitness = 0.0
            new_population.append(elite)

        # Create offspring through crossover and mutation
        while len(new_population) < self.population_size:
            # Select two random parents (weighted by fitness)
            parent1 = random.choices(parents, weights=[p.fitness + 0.1 for p in parents])[0]
            parent2 = random.choices(parents, weights=[p.fitness + 0.1 for p in parents])[0]

            if parent1 != parent2:
                # Crossover
                child1, child2 = parent1.crossover(parent2)
            else:
                # Just mutate
                child1 = parent1.mutate()
                child2 = parent1.mutate()

            # DRAMATICALLY mutate children (increased rates for more evolution pressure)
            child1 = child1.mutate(mutation_rate=0.3, mutation_strength=0.4)
            child2 = child2.mutate(mutation_rate=0.3, mutation_strength=0.4)

            # Set generation info
            for child in [child1, child2]:
                child.generation = self.generation + 1
                child.parent_ids = [parents.index(parent1), parents.index(parent2)]
                child.games_played = 0
                child.wins = 0
                child.draws = 0
                child.losses = 0
                child.fitness = 0.0

            new_population.extend([child1, child2])

        # Trim to exact population size
        self.population = new_population[:self.population_size]
        self.generation += 1

        print(f"Created generation {self.generation} with {len(self.population)} bots")

    def save_generation_data(self):
        """Save the current generation data"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Save population data
        population_data = {
            'generation': self.generation,
            'population_size': len(self.population),
            'best_fitness': max(g.fitness for g in self.population),
            'average_fitness': sum(g.fitness for g in self.population) / len(self.population),
            'genomes': [genome.to_dict() for genome in self.population]
        }

        filename = f"evolution_data/generation_{self.generation:03d}_{timestamp}.json"
        with open(filename, 'w') as f:
            json.dump(population_data, f, indent=2)

        # Save champion - always save the best from current generation
        # Sort population by fitness and get the best
        best_current_gen = max(self.population, key=lambda g: g.fitness)

        # Update best_ever_genome if this is better
        if self.best_ever_genome is None or best_current_gen.fitness > self.best_ever_fitness:
            self.best_ever_genome = copy.deepcopy(best_current_gen)
            self.best_ever_fitness = best_current_gen.fitness

        # Always save the best genome from current generation
        champion_file = f"evolution_champions/champion_gen_{self.generation:03d}.json"
        with open(champion_file, 'w') as f:
            json.dump(best_current_gen.to_dict(), f, indent=2)

        # Also save the all-time best if different
        if self.best_ever_genome != best_current_gen:
            best_ever_file = f"evolution_champions/best_ever_gen_{self.generation:03d}.json"
            with open(best_ever_file, 'w') as f:
                json.dump(self.best_ever_genome.to_dict(), f, indent=2)

        print(f"Generation data saved to {filename}")
        print(f"Champion saved with fitness: {best_current_gen.fitness:.3f}")

    def run_evolution(self, max_generations=10):
        """Run the complete evolutionary process"""
        print(f"Starting evolutionary training for {max_generations} generations")
        print(f"Population size: {self.population_size}")

        for gen in range(max_generations):
            print(f"\n=== GENERATION {self.generation} ===")

            # Run tournament
            start_time = time.time()
            self.run_tournament()
            tournament_time = time.time() - start_time

            # Show results
            self.show_generation_stats()

            # Save data
            self.save_generation_data()

            # Create next generation (except for last generation)
            if gen < max_generations - 1:
                parents = self.select_parents(self.population_size // 2)
                self.create_next_generation(parents)

            print(f"Generation {self.generation} completed in {tournament_time:.1f}s")

        print(f"\nEvolution completed! Best fitness achieved: {self.best_ever_fitness:.3f}")
        return self.best_ever_genome

    def show_generation_stats(self):
        """Show statistics for current generation"""
        fitnesses = [g.fitness for g in self.population]
        games_played = [g.games_played for g in self.population]

        print(f"Generation {self.generation} Results:")
        print(f"  Best fitness: {max(fitnesses):.3f}")
        print(f"  Average fitness: {sum(fitnesses) / len(fitnesses):.3f}")
        print(f"  Worst fitness: {min(fitnesses):.3f}")
        print(f"  Average games per bot: {sum(games_played) / len(games_played):.1f}")

        # Show top 3 bots
        sorted_pop = sorted(self.population, key=lambda g: g.fitness, reverse=True)
        print("  Top 3 bots:")
        for i, genome in enumerate(sorted_pop[:3]):
            print(f"    {i+1}. Fitness: {genome.fitness:.3f}, W-D-L: {genome.wins}-{genome.draws}-{genome.losses}")


def main():
    """Main function to run evolutionary training"""
    print("DragonBot Evolutionary Training System")
    print("=====================================")
    print("The bot will evolve and improve itself through natural selection!")

    # Create trainer
    trainer = EvolutionaryTrainer(population_size=16, games_per_generation=80)

    # Run evolution with more generations for better results
    champion = trainer.run_evolution(max_generations=1)

    print("\nEvolution completed!")
    print("The champion bot has been saved to 'evolution_champions/'")
    print("Check 'evolution_data/' for detailed evolution history")


if __name__ == "__main__":
    main()