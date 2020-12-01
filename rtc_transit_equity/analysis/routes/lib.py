

# route_names = list(set(result.route_long_name))

# # TODO FIGURE OUT WHY WE HAVE DUPLICATE AGENCIES
# # Normalize route's median household income by bus stops along the route
# averages = {}
# for route_name in route_names:
#     route_stops = result.loc[result.route_long_name == route_name]
#     route_avg = (route_stops.population * route_stops.median_household_income).sum() / route_stops.population.sum()
    
#     agencies = list(set(route_stops.Agency))
#     averages[route_name] = {
#         "median_household_income": float(route_avg), 
#         "RTA": list(set(route_stops.Agency)),
#         "route_population": float(route_stops.population.sum()),
#         "short_name": list(set(route_stops.route_short_name))
#     }
