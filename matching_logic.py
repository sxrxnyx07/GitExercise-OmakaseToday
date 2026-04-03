def check_match(user_ingredients,recipe_ingredients):

    # Convert lists to sets 
    user_set = set(user_ingredients)
    recipe_set = set(recipe_ingredients)

    # Find what matches
    matches = user_set.intersection(recipe_set)

    # Find what is missing
    missing = recipe_set - user_set

    # Calculate percentage
    match_percentage = (len(matches) / len(recipe_set)) * 100

    return round(match_percentage,2) , list(missing)

# Example Test
my_kitchen = ["eggs" , "milk" , "flour"]
pancake_recipe = ["eggs" , "milk" , "flour" , "butter" , "syrup" ]

percent, need_to_buy = check_match(my_kitchen, pancake_recipe)

print(f"Match: {percent}%")
print(f"Still need: {need_to_buy}")
