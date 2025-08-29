"""
Evolutionary Self-Play Training System for DragonBot

Creates multiple parameter variants (genomes), has them self-play, and evolves better ones.
"""
import chess
import random
import time
import json
import os
import copy
from datetime import datetime
from pathlib import Path
from engines.bot.main import get_move


BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "evolution_data"
CHAMPIONS_DIR = BASE_DIR / "evolution_champions"


class BotGenome:
    """Genome containing tunable parameters and stats."""

    def __init__(self):
        self.piece_values = {'pawn': 100, 'knight': 310, 'bishop': 330, 'rook': 500, 'queen': 900, 'king': 20000}
        self.eval_weights = {
            'material_weight': 1.0, 'position_weight': 0.3, 'king_safety_weight': 0.8,
            'pawn_structure_weight': 0.4, 'piece_activity_weight': 0.6, 'center_control_weight': 0.5,
            'development_bonus': 10, 'castling_bonus': 20, 'doubled_pawn_penalty': 20,
            'isolated_pawn_penalty': 15, 'rook_open_file_bonus': 35
        }
        self.search_params = {'base_depth': 4, 'quiescence_depth': 10, 'aggressive_factor': 1.0, 'safety_factor': 1.0}
        self.style_params = {'randomness_opening': 0.1, 'randomness_middlegame': 0.05, 'randomness_endgame': 0.02, 'risk_tolerance': 0.5}
        self.fitness = 0.0
        self.games_played = self.wins = self.draws = self.losses = 0
        self.generation = 0
        self.parent_ids: list[int] = []

    def mutate(self, mutation_rate=0.4, mutation_strength=0.6):
        """Return a mutated copy of this genome (includes occasional radical changes)."""
        new_genome = copy.deepcopy(self)
        radical_mutation_chance = 0.15
        # Piece values
        for piece, current_value in list(new_genome.piece_values.items()):
            if piece == 'king' or random.random() >= mutation_rate:
                continue
            if random.random() < 0.3:  # replace within sensible bounds
                ranges = {
                    'pawn': (50, 200), 'knight': (200, 500), 'bishop': (200, 500),
                    'rook': (300, 700), 'queen': (600, 1200)
                }
                lo, hi = ranges[piece]
                new_genome.piece_values[piece] = random.randint(lo, hi)
            else:
                change = random.uniform(-mutation_strength, mutation_strength)
                new_genome.piece_values[piece] = max(10, int(current_value * (1 + change)))
        # Evaluation weights
        for param, current_value in list(new_genome.eval_weights.items()):
            if random.random() >= mutation_rate:
                continue
            if random.random() < 0.25:  # radical reset
                if 'weight' in param:
                    new_genome.eval_weights[param] = random.uniform(0.1, 3.0)
                elif 'bonus' in param or 'penalty' in param:
                    new_genome.eval_weights[param] = random.randint(5, 50)
                else:
                    new_genome.eval_weights[param] = random.uniform(0.1, 2.0)
            else:
                change = random.uniform(-mutation_strength, mutation_strength)
                new_genome.eval_weights[param] = max(0.01, current_value * (1 + change))
        # Search depth tweaks
        if random.random() < mutation_rate * 1.5:
            if random.random() < 0.3:
                new_genome.search_params['base_depth'] = random.choice([2, 3, 4, 5, 6])
            else:
                new_genome.search_params['base_depth'] = max(2, min(6, new_genome.search_params['base_depth'] + random.choice([-2, -1, 0, 1, 2])))
        if random.random() < mutation_rate:
            if random.random() < 0.2:
                new_genome.search_params['quiescence_depth'] = random.randint(5, 20)
            else:
                change = random.uniform(-0.5, 0.5)
                qd = int(new_genome.search_params['quiescence_depth'] * (1 + change))
                new_genome.search_params['quiescence_depth'] = max(3, min(20, qd))
        for param in ['aggressive_factor', 'safety_factor']:
            if random.random() < mutation_rate:
                current = new_genome.search_params[param]
                if random.random() < 0.2:
                    new_genome.search_params[param] = random.uniform(0.2, 3.0)
                else:
                    change = random.uniform(-mutation_strength, mutation_strength)
                    new_genome.search_params[param] = max(0.1, min(3.0, current * (1 + change)))
        # Style
        for param, current in list(new_genome.style_params.items()):
            if random.random() >= mutation_rate * 1.2:
                continue
            if 'randomness' in param:
                if random.random() < 0.25:
                    new_genome.style_params[param] = random.uniform(0.0, 0.8)
                else:
                    change = random.uniform(-mutation_strength, mutation_strength)
                    new_genome.style_params[param] = max(0.0, min(1.0, current * (1 + change)))
            elif param == 'risk_tolerance':
                if random.random() < 0.3:
                    new_genome.style_params[param] = random.uniform(0.0, 1.0)
                else:
                    change = random.uniform(-mutation_strength, mutation_strength)
                    new_genome.style_params[param] = max(0.0, min(1.0, current * (1 + change)))
        # Occasional radical changes
        if random.random() < radical_mutation_chance:
            pieces = ['pawn', 'knight', 'bishop', 'rook', 'queen']
            a, b = random.sample(pieces, 2)
            if {'pawn','queen'} != {a,b}:  # avoid absurd pawn>queen swap
                new_genome.piece_values[a], new_genome.piece_values[b] = new_genome.piece_values[b], new_genome.piece_values[a]
        if random.random() < radical_mutation_chance:
            if random.random() < 0.5:
                af, sf = new_genome.search_params['aggressive_factor'], new_genome.search_params['safety_factor']
                new_genome.search_params['aggressive_factor'], new_genome.search_params['safety_factor'] = sf, af
            else:
                new_genome.style_params['risk_tolerance'] = 1.0 - new_genome.style_params['risk_tolerance']
        if random.random() < radical_mutation_chance * 0.5:
            new_genome.style_params['randomness_opening'] = random.uniform(0.0, 0.5)
            new_genome.style_params['randomness_middlegame'] = random.uniform(0.0, 0.3)
            new_genome.style_params['randomness_endgame'] = random.uniform(0.0, 0.2)
        if random.random() < radical_mutation_chance * 0.7:
            focus = random.choice(['king_safety_weight','pawn_structure_weight','piece_activity_weight','center_control_weight'])
            for p in ['king_safety_weight','pawn_structure_weight','piece_activity_weight','center_control_weight']:
                if p == focus:
                    new_genome.eval_weights[p] *= random.uniform(2.0, 4.0)
                else:
                    new_genome.eval_weights[p] *= random.uniform(0.5, 0.8)
        return new_genome

    def crossover(self, other_genome):
        """Combine this genome with another to create two offspring."""
        child1 = copy.deepcopy(self)
        child2 = copy.deepcopy(other_genome)
        mixing_rate = 0.7
        # Piece values
        for piece in child1.piece_values:
            if random.random() < mixing_rate:
                if random.random() < 0.3:
                    avg = (child1.piece_values[piece] + child2.piece_values[piece]) // 2
                    var = random.uniform(0.8, 1.2)
                    child1.piece_values[piece] = int(avg * var)
                    child2.piece_values[piece] = int(avg * (2 - var))
                else:
                    child1.piece_values[piece], child2.piece_values[piece] = child2.piece_values[piece], child1.piece_values[piece]
        # Eval weights
        for param in child1.eval_weights:
            if random.random() < mixing_rate:
                if random.random() < 0.4:
                    avg = (child1.eval_weights[param] + child2.eval_weights[param]) / 2
                    var = random.uniform(0.6, 1.4)
                    child1.eval_weights[param] = max(0.01, avg * var)
                    child2.eval_weights[param] = max(0.01, avg * (2 - var))
                else:
                    child1.eval_weights[param], child2.eval_weights[param] = child2.eval_weights[param], child1.eval_weights[param]
        # Search params
        for param in child1.search_params:
            if random.random() >= mixing_rate:
                continue
            if param == 'base_depth':
                if random.random() < 0.5:
                    child1.search_params[param], child2.search_params[param] = child2.search_params[param], child1.search_params[param]
                else:
                    avg = (child1.search_params[param] + child2.search_params[param]) / 2
                    child1.search_params[param] = max(2, min(6, int(avg + random.choice([-1,0,1]))))
                    child2.search_params[param] = max(2, min(6, int(avg + random.choice([-1,0,1]))))
            elif param == 'quiescence_depth':
                if random.random() < 0.5:
                    child1.search_params[param], child2.search_params[param] = child2.search_params[param], child1.search_params[param]
                else:
                    avg = (child1.search_params[param] + child2.search_params[param]) / 2
                    child1.search_params[param] = max(3, min(20, int(avg * random.uniform(0.8,1.2))))
                    child2.search_params[param] = max(3, min(20, int(avg * random.uniform(0.8,1.2))))
            else:
                if random.random() < 0.3:
                    avg = (child1.search_params[param] + child2.search_params[param]) / 2
                    var = random.uniform(0.7,1.3)
                    child1.search_params[param] = max(0.1, min(3.0, avg * var))
                    child2.search_params[param] = max(0.1, min(3.0, avg * (2 - var)))
                else:
                    child1.search_params[param], child2.search_params[param] = child2.search_params[param], child1.search_params[param]
        # Style params
        for param in child1.style_params:
            if random.random() < mixing_rate * 1.1:
                if random.random() < 0.4:
                    avg = (child1.style_params[param] + child2.style_params[param]) / 2
                    var = random.uniform(0.6, 1.4)
                    child1.style_params[param] = max(0.0, min(1.0, avg * var))
                    child2.style_params[param] = max(0.0, min(1.0, avg * (2 - var)))
                else:
                    child1.style_params[param], child2.style_params[param] = child2.style_params[param], child1.style_params[param]
        # Extra variation
        if random.random() < 0.2:
            for param in child1.eval_weights:
                vals = [self.eval_weights[param], other_genome.eval_weights[param]]
                if min(vals) > 0 and max(vals)/min(vals) > 2.0:
                    child1.eval_weights[param] = max(vals) * random.uniform(1.0,1.5)
                    child2.eval_weights[param] = min(vals) * random.uniform(0.5,1.0)
        if random.random() < 0.15:
            for param in child1.style_params:
                base = (self.style_params[param] + other_genome.style_params[param]) / 2
                child1.style_params[param] = max(0.0, min(1.0, base + random.uniform(-0.2,0.2)))
                child2.style_params[param] = max(0.0, min(1.0, base + random.uniform(-0.2,0.2)))
        return child1, child2

    def calculate_fitness(self):
        if self.games_played == 0:
            self.fitness = 0.0
            return 0.0
        self.fitness = (self.wins / self.games_played) + 0.5 * (self.draws / self.games_played)
        return self.fitness

    def update_results(self, result):
        self.games_played += 1
        if result == 1: self.wins += 1
        elif result == 0: self.draws += 1
        else: self.losses += 1
        self.calculate_fitness()

    def to_dict(self):
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

        # Create directories (now relative to this module's folder)
        os.makedirs(DATA_DIR, exist_ok=True)
        os.makedirs(CHAMPIONS_DIR, exist_ok=True)

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
        """Play a game between two bots with explicit move logging."""
        board = chess.Board()
        move_count = 0
        max_moves = 200
        try:
            while not board.is_game_over() and move_count < max_moves:
                current_bot = bot1 if board.turn == chess.WHITE else bot2
                side = 'White' if board.turn == chess.WHITE else 'Black'
                move = current_bot.get_move(board, time_limit=3.0)
                if move not in board.legal_moves:
                    move = random.choice(list(board.legal_moves))
                board.push(move)
                move_count += 1
                # Log move with ply and FEN for debugging alternation issues
                print(f"Ply {move_count:03d} | {side} played {move.uci()} | FEN: {board.fen()}")
            if board.is_checkmate():
                return -1 if board.turn == chess.WHITE else 1
            return 0
        except Exception as e:
            print(f"Error in game {game_id}: {e}")
            return 0

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

        filename = DATA_DIR / f"generation_{self.generation:03d}_{timestamp}.json"
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
        champion_file = CHAMPIONS_DIR / f"champion_gen_{self.generation:03d}.json"
        with open(champion_file, 'w') as f:
            json.dump(best_current_gen.to_dict(), f, indent=2)

        # Also save the all-time best if different
        if self.best_ever_genome != best_current_gen:
            best_ever_file = CHAMPIONS_DIR / f"best_ever_gen_{self.generation:03d}.json"
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
    print("The champion bot has been saved to 'self_learning/evolution_champions/'")
    print("Check 'self_learning/evolution_data/' for detailed evolution history")


if __name__ == "__main__":
    main()