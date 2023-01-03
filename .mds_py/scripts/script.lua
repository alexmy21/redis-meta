-- script.lua
local sum_of_new_list = 0

-- Pushing the new_list to the redis list 
-- Also calculating the sum of the new_list
for key,value in ipairs(ARGV) do
    sum_of_new_list = sum_of_new_list + tonumber(value)
    redis.call('LPUSH', KEYS[1], value)
end

-- Incrementing the value of the redis key "sum" by the sum_of_new_list
local total_sum = redis.call('INCRBY', KEYS[2], sum_of_new_list)

-- Finally returning the total_sum
return total_sum