# Learning-Based Cache Eviction
This is our comp arch final project! 
We used deep learning for cache replacement, which we integrated into our verilog pipeline processor (which we cannot post because it's class material). We generated data by running algorithms (quicksort, binary search) using our verilog processor and recording all the memory access patterns. We used this data to generate sequences of loads for training.
We used this data to train an RNN to predict access patterns. We integrated this model into our pipeline using a python cpu emulator and cache module.
