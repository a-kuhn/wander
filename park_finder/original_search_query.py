    allows_pets = request.POST['allows_pets']
    limited_access = request.POST['limited_access']
    busy = request.POST['busy']
    has_shade = request.POST['has_shade']
    has_water = request.POST['has_water']
    has_bathrooms = request.POST['has_bathrooms']
    is_accessible = request.POST['is_accessible']
    is_kid_friendly = request.POST['is_kid_friendly']
    has_playground = request.POST['has_playground']

    search_results = Park.objects.filter(allows_pets = allows_pets).filter(limited_access = limited_access).filter(busy = busy).filter(has_shade = has_shade).filter(has_water = has_water).filter(has_bathrooms = has_bathrooms).filter(is_accessible = is_accessible).filter(is_kid_friendly = is_kid_friendly).filter(has_playground = has_playground)

    activity_match = []
    activity_no_match = []
    feature_match = []
    feature_no_match = []

    for park in search_results:
        possible_activities = [item.strip() for item in park.permitted_activities.split(',')]
        print("*-"*15,"\npark: ",park, "\npossible activities: ", possible_activities, "\ntype p_a: ",type(possible_activities))
        for activity in formatted_activities:
            print("activity:", activity)
            if activity in possible_activities:
                print("\npossible activities",possible_activities)
                activity_match.append(activity)
            elif activity not in possible_activities:
                activity_no_match.append(activity)
            print("*-"*15, "\nactivity match: ", activity_match, "\nactivity_no_match: ",activity_no_match)
    for park in search_results:
        possible_features = [item.strip() for item in park.natural_features.split(',')]
        for feature in formatted_features:
            print("feature:", feature)
            if feature in possible_features:
                feature_match.append(feature)
            elif feature not in possible_features:
                feature_no_match.append(feature)
        print("*-"*15, "\nfeature match: ", feature_match, "\nfeature_no_match: ",feature_no_match)

    # >>removed from context
        "search_results": search_results,
        "activity_match": activity_match,
        "activity_no_match": activity_no_match,
        "feature_match": feature_match,
        "feature_no_match": feature_no_match,