# optimisers.py

import random

class RandomOptimiser:
    def __init__(self, build_fn, param_names, param_init, vary_mask, bounds, cost_fn, 
                 delta_init=0.2, stall_limit=50, max_iter=1000):
        self.build_fn = build_fn
        self.param_names = param_names
        self.x_baseline = param_init.copy()
        self.vary_mask = vary_mask
        self.bounds = bounds
        self.cost_fn = cost_fn
        self.delta_x = delta_init
        self.stall_limit = stall_limit
        self.max_iter = max_iter

    def random_variation(self, x):
        x_new = x.copy()
        for name in self.param_names:
            if self.vary_mask.get(name, False):
                factor = 1 + random.uniform(-self.delta_x, self.delta_x)
                val = x[name] * factor
                minv, maxv = self.bounds[name]
                x_new[name] = max(min(val, maxv), minv)
        return x_new

    def optimise(self, verbose=False):
        best_params = self.x_baseline.copy()
        best_model = self.build_fn(**best_params)
        best_model.write_nec_and_run()
        result = self.cost_fn(best_model)
        best_cost = result['cost']
        best_info = result['info']
        stall_count = 0
        if verbose:
            formatted_params = {k: round(v, 2) for k, v in best_params.items()}
            print(f"[] INITIAL: {best_info} with {formatted_params}")

        for i in range(self.max_iter):
            test_params = self.random_variation(best_params)
            test_model = self.build_fn(**test_params)
            test_model.write_nec_and_run()
            result = self.cost_fn(test_model)
            test_cost = result['cost']
            test_info = result['info']

            if test_cost < best_cost:
                best_cost = test_cost
                best_params = test_params
                best_info = test_info
                stall_count = 0
                if verbose:
                    formatted_params = {k: round(v, 2) for k, v in best_params.items()}
                    print(f"[{i}] IMPROVED: {best_info} with {formatted_params}")

            else:
                stall_count += 1
                if verbose:
                    print(f"[{i}] {test_info}")

            if stall_count >= self.stall_limit:
                self.delta_x /= 2
                stall_count = 0
                if verbose:
                    print(f"[{i}] Reducing delta to {self.delta_x}")

        best_model = self.build_fn(**best_params)
        best_model.write_nec_and_run()
        result = self.cost_fn(best_model)
        final_info = result['info']
        formatted_params = {k: round(v, 2) for k, v in best_params.items()}
        return formatted_params, final_info
