import random
import model
import torch

class Cache:

    CACHE_SIZE = 1500
    HISTORY_SIZE = 100
    MAX = 10000000

    # FIFO cache
    fifo_cache_addrs = []
    fifo_cache_values = []
    fifo_cache_hits = 0

    # RRPV cache
    load_history = []
    rrpv_cache_addrs = []
    rrpv_cache_values = []
    rrpv_preds = []
    rrpv_cache_hits = 0

    #prediction model
    prediction_model = model.Model(input_size=100, output_size=1, hidden_dim=10, n_layers=1)
    prediction_model.load_state_dict(torch.load("model", map_location=torch.device('cpu')))
    prediction_model.eval()

    # TODO: where should this be incremented
    memory_lookups = 0


    def cache_lookup(self, memory_addr, my_mem):
        Cache.memory_lookups += 1
        self.fifo_cache_lookup(memory_addr, my_mem)
        self.rrpv_cache_lookup(memory_addr, my_mem)


    def fifo_cache_lookup(self, memory_addr, my_mem):
        
        # if value is already in cache
        if memory_addr in Cache.fifo_cache_addrs:
            Cache.fifo_cache_hits += 1
            
            # look up cached value
            position = Cache.fifo_cache_addrs.index(memory_addr)
            val = Cache.fifo_cache_values[position]
            
            # move memory_addr to end of queue
            # Cache.fifo_cache_addrs.append(Cache.fifo_cache_addrs.pop(position))
            # Cache.fifo_cache_values.append(Cache.fifo_cache_values.pop(position))

            return val
            
        # if value is not in cache and cache is full
        if (len(Cache.fifo_cache_addrs) == Cache.CACHE_SIZE):
            # remove old values
            Cache.fifo_cache_addrs.pop(0)
            Cache.fifo_cache_values.pop(0)
        
        # add new values
        Cache.fifo_cache_addrs.append(memory_addr)
        Cache.fifo_cache_values.append(my_mem[memory_addr])

        return my_mem[memory_addr]


    def rrpv_cache_lookup(self, memory_addr, my_mem):
        
        # update load history
        if (len(Cache.load_history) == Cache.HISTORY_SIZE):
            Cache.load_history.pop(0)
        Cache.load_history.append(memory_addr)

        # if value is already in cache
        if memory_addr in Cache.rrpv_cache_addrs:
            Cache.rrpv_cache_hits += 1
            
            # look up cached value
            position = Cache.rrpv_cache_addrs.index(memory_addr)
            val = Cache.rrpv_cache_values[position]

            # update rrpv values
            rrpv = self.predict_rrpv(memory_addr)
            Cache.rrpv_preds[position] = rrpv

            return val
        
        # if value is not in cache

        # if cache is full, evict using rrpv
        if (len(Cache.fifo_cache_addrs) == Cache.CACHE_SIZE):
            # calculate difference between Cache.MAX and current set of RRPVs
            MAX_rrpv = max(Cache.rrpv_preds)
            diff = Cache.MAX - MAX_rrpv
            # increase all the elements currenlty in the cache by diff
            Cache.rrpv_preds = [Cache.rrpv_preds[i] + diff for i in range(len(Cache.rrpv_preds))]
            # evict the first value with rrpv == Cache.MAX
            evict_val_index = Cache.rrpv_preds.index(Cache.MAX)
            Cache.rrpv_cache_addrs.pop(evict_val_index)
            Cache.rrpv_cache_values.pop(evict_val_index)
            Cache.rrpv_preds.pop(evict_val_index)

        # add new value with associated rrpv
        Cache.rrpv_cache_addrs.append(memory_addr)
        Cache.rrpv_cache_values.append(my_mem[memory_addr])
        Cache.rrpv_preds.append(self.predict_rrpv(memory_addr))

        return my_mem[memory_addr]


    def predict_rrpv(self, memory_addr):
        # TODO: use model
        # return random.randint(0, 10000)
        if len(Cache.load_history) < Cache.HISTORY_SIZE:
            extended_load_history = [0] * (Cache.HISTORY_SIZE - len(Cache.load_history)) + Cache.load_history
        else:
            extended_load_history = Cache.load_history
        X = torch.Tensor([extended_load_history])
        return model.inv_normalize(Cache.prediction_model(X)[0][0][0].item())


    def update_cache(self, memory_addr, val):
        # update fifo cache
        if memory_addr in Cache.fifo_cache_addrs:
            fifo_index = Cache.fifo_cache_addrs.index(memory_addr)
            Cache.fifo_cache_values[fifo_index] = val
        
        # rrpv cache
        if memory_addr in Cache.rrpv_cache_addrs:
            rrpv_index = Cache.rrpv_cache_addrs.index(memory_addr)
            Cache.rrpv_cache_values[rrpv_index] = val


    def cache_accuracy(self):
        fifo_accuracy = Cache.fifo_cache_hits/Cache.memory_lookups
        rrpv_accuracy = Cache.rrpv_cache_hits/Cache.memory_lookups
        return (fifo_accuracy, rrpv_accuracy)


