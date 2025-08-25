from books.models import Book
from reviews.models import Review
from django.db.models import Count, Q

def get_content_based_recommendations(user, num_recommendations=10):
    """
    Generates content-based book recommendations for a user.

    The algorithm recommends books based on the genres and authors of books the
    user has positively reviewed (rating >= 4).

    Args:
        user: The user for whom to generate recommendations.
        num_recommendations (int): The number of recommendations to return.

    Returns:
        A queryset of recommended Book objects.
    """
    # Get books the user has positively reviewed
    positive_reviews = Review.objects.filter(user=user, rating__gte=4)
    if not positive_reviews.exists():
        return Book.objects.none()

    # Get the IDs of books the user has reviewed
    reviewed_book_ids = positive_reviews.values_list('book__id', flat=True)

    # Get the genres and authors from the user's liked books
    liked_genres = set(positive_reviews.values_list('book__genres__id', flat=True))
    liked_authors = set(positive_reviews.values_list('book__authors__id', flat=True))

    # Find books with similar genres or authors
    recommended_books = Book.objects.filter(
        Q(genres__id__in=liked_genres) | Q(authors__id__in=liked_authors)
    ).exclude(
        id__in=reviewed_book_ids
    ).distinct()

    # Rank books by the number of shared genres and authors
    recommended_books = recommended_books.annotate(
        shared_genres=Count('genres', filter=Q(genres__id__in=liked_genres)),
        shared_authors=Count('authors', filter=Q(authors__id__in=liked_authors))
    ).order_by(
        '-shared_genres', '-shared_authors', '-sold_count'
    )

    return recommended_books[:num_recommendations]


from django.contrib.auth import get_user_model

def get_collaborative_filtering_recommendations(user, num_recommendations=10):
    """
    Generates user-based collaborative filtering recommendations for a user.

    This algorithm finds users with similar tastes and recommends books that
    they have liked.

    Args:
        user: The user for whom to generate recommendations.
        num_recommendations (int): The number of recommendations to return.

    Returns:
        A queryset of recommended Book objects.
    """
    User = get_user_model()

    # Get all reviews from the current user
    user_reviews = Review.objects.filter(user=user)
    if not user_reviews.exists():
        return Book.objects.none()

    user_reviewed_books_ids = user_reviews.values_list('book__id', flat=True)

    # Find users who have reviewed the same books
    similar_users = User.objects.filter(
        reviews__book__id__in=user_reviewed_books_ids
    ).exclude(id=user.id).distinct()

    # If no similar users, we can't make a recommendation
    if not similar_users.exists():
        return Book.objects.none()

    # Annotate users with the number of co-reviewed books
    similar_users = similar_users.annotate(
        shared_books_count=Count('reviews', filter=Q(reviews__book__id__in=user_reviewed_books_ids))
    ).order_by('-shared_books_count')

    # Consider top 10 most similar users
    top_similar_users = similar_users[:10]
    top_similar_user_ids = [u.id for u in top_similar_users]

    # Get books liked by these similar users
    recommended_books = Book.objects.filter(
        reviews__user__id__in=top_similar_user_ids,
        reviews__rating__gte=4
    ).exclude(
        id__in=user_reviewed_books_ids
    ).distinct()

    # Rank books by how many similar users liked them
    recommended_books = recommended_books.annotate(
        recommendation_score=Count('reviews', filter=Q(reviews__user__id__in=top_similar_user_ids))
    ).order_by('-recommendation_score', '-sold_count')

    return recommended_books[:num_recommendations]


def get_hybrid_recommendations(user, num_recommendations=10):
    """
    Generates hybrid book recommendations for a user.

    This algorithm combines content-based and collaborative filtering
    recommendations to provide a more diverse and accurate list.

    Args:
        user: The user for whom to generate recommendations.
        num_recommendations (int): The number of recommendations to return.

    Returns:
        A list of recommended Book objects.
    """
    # Get recommendations from both algorithms
    content_based_recs = get_content_based_recommendations(user, num_recommendations)
    collaborative_recs = get_collaborative_filtering_recommendations(user, num_recommendations)

    # Combine the recommendations
    hybrid_recs = list(content_based_recs) + list(collaborative_recs)

    # Remove duplicates, preserving order
    seen = set()
    unique_recs = []
    for book in hybrid_recs:
        if book.id not in seen:
            unique_recs.append(book)
            seen.add(book.id)

    # If we don't have enough recommendations, fill with popular books
    if len(unique_recs) < num_recommendations:
        popular_books = Book.objects.order_by('-sold_count').exclude(id__in=seen)
        for book in popular_books:
            if len(unique_recs) >= num_recommendations:
                break
            if book.id not in seen:
                unique_recs.append(book)
                seen.add(book.id)

    return unique_recs[:num_recommendations]
