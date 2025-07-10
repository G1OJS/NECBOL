"""
This file is part of the "NECBOL Plain Language Python NEC Runner"
Copyright (c) 2025 Alan Robinson G1OJS

MIT License

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import random

class RandomOptimiser:
    def __init__(self, build_fn, param_init, cost_fn,
                 bounds={}, delta_init=0.2, stall_limit=50, max_iter=250, min_delta=0.001):
        self.build_fn = build_fn
        self.param_names = list(param_init.keys())
        self.x_baseline = param_init.copy()
        self.bounds = bounds
        self.cost_fn = cost_fn
        self.delta_x = delta_init
        self.min_delta = min_delta
        self.stall_limit = stall_limit
        self.max_iter = max_iter

    def format_params(self, params):
        s="{"
        for k, v in params.items():
            s = s + f"'{k}': {v:.2f}, "
        return s[0:-2]+"}"

    def random_variation(self, x):
        x_new = x.copy()
        for name in self.param_names:
            factor = 1 + random.uniform(-self.delta_x, self.delta_x)
            val = x[name] * factor
            x_new[name] = val
            if(name in self.bounds):
                minv, maxv = self.bounds[name]
                x_new[name] = max(min(x_new[name], maxv), minv)
        return x_new

    def optimise(self, model,  verbose=False):
        best_params = self.x_baseline.copy()
        best_model = self.build_fn(model, **best_params)
        best_model.write_nec()
        best_model.run_nec()
        result = self.cost_fn(best_model)
        best_cost = result['cost']
        best_info = result['info']
        stall_count = 0
        initial_message = f"[] INITIAL: {best_info} with {self.format_params(best_params)}"
        print(initial_message)

        for i in range(self.max_iter):
            test_params = self.random_variation(best_params)
            test_model = self.build_fn(model, **test_params)
            test_model.write_nec()
            test_model.run_nec()
            result = self.cost_fn(test_model)
            test_cost = result['cost']
            test_info = result['info']

            if test_cost < best_cost:
                best_cost = test_cost
                best_params = test_params
                best_info = test_info
                stall_count = 0
                print(f"[{i}] IMPROVED: {best_info} with {self.format_params(best_params)}")
            else:
                stall_count += 1
                if (verbose):
                    print(f"[{i}] {test_info} with {self.format_params(test_params)}")
                else:
                    print(f"[{i}] {test_info}")

            if stall_count >= self.stall_limit:
                self.delta_x /= 2
                if(self.delta_x < self.min_delta):
                    print(f"[{i}] Delta below minimum")
                    break
                stall_count = 0
                print(f"[{i}] Reducing delta to {self.delta_x}")


        best_model = self.build_fn(model, **best_params)
        best_model.write_nec()
        best_model.run_nec()
        result = self.cost_fn(best_model)
        final_info = result['info']
        print("# Optimiser Results (copy and paste into your antenna file for reference)")
        print("# "+ initial_message)
        print(f"# []   FINAL: {final_info} with {self.format_params(best_params)}")

        return best_params, final_info
