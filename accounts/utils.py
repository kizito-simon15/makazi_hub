import base64
import io
import datetime
from django.utils import timezone
import matplotlib.pyplot as plt
from django.contrib.auth import get_user_model
from accounts.models import PropertyOwner, Client
from owners.models import Agent

def get_growth_data():
    """
    Collect the number of users, property owners, clients, and agents over time.
    We will consider a time window (e.g., the last 6 months) and count how many joined each month.
    """
    User = get_user_model()

    # Define the time range (e.g., last 6 months)
    end_date = timezone.now()
    start_date = end_date - datetime.timedelta(days=180)  # last 6 months roughly

    # Prepare containers for data
    # We'll store data monthly
    dates = []
    user_counts = []
    owner_counts = []
    client_counts = []
    agent_counts = []

    # We'll iterate month by month
    current_date = start_date
    while current_date <= end_date:
        # month start and end
        month_start = current_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        # next month
        if month_start.month == 12:
            next_month = month_start.replace(year=month_start.year+1, month=1)
        else:
            next_month = month_start.replace(month=month_start.month+1)

        # Filter users by date_joined
        monthly_users = User.objects.filter(date_joined__gte=month_start, date_joined__lt=next_month).count()
        monthly_owners = PropertyOwner.objects.filter(user__date_joined__gte=month_start, user__date_joined__lt=next_month).count()
        monthly_clients = Client.objects.filter(user__date_joined__gte=month_start, user__date_joined__lt=next_month).count()
        monthly_agents = Agent.objects.filter(created_at__gte=month_start, created_at__lt=next_month).count()

        dates.append(month_start.strftime("%b %Y"))
        user_counts.append(monthly_users)
        owner_counts.append(monthly_owners)
        client_counts.append(monthly_clients)
        agent_counts.append(monthly_agents)

        # Move to next month
        current_date = next_month

    return dates, user_counts, owner_counts, client_counts, agent_counts

def generate_growth_chart():
    """
    Generates a line graph of user growth data over time.
    Returns a base64 encoded PNG image and advice string.
    """
    dates, user_counts, owner_counts, client_counts, agent_counts = get_growth_data()

    # Create a figure and plot
    plt.figure(figsize=(10, 5))
    plt.plot(dates, user_counts, marker='o', label='Total Users')
    plt.plot(dates, owner_counts, marker='o', label='Owners')
    plt.plot(dates, client_counts, marker='o', label='Clients')
    plt.plot(dates, agent_counts, marker='o', label='Agents')

    plt.title("Growth of the Application's User Base Over Time")
    plt.xlabel("Month")
    plt.ylabel("Number of New Users Joined")
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()

    # Save plot to a bytes buffer
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)

    # Encode the image to base64
    image_png = buffer.getvalue()
    buffer.close()
    plt.close()

    image_base64 = base64.b64encode(image_png).decode('utf-8')

    # Generate advice based on growth trends
    # Simple heuristic: Calculate average growth of total users
    # If growth is consistently rising, give positive advice
    # If growth is stagnating or declining, give suggestions.
    # We'll use user_counts as a primary metric.
    if len(user_counts) > 1:
        # Compute growth differences
        differences = [user_counts[i] - user_counts[i-1] for i in range(1, len(user_counts))]
        avg_growth = sum(differences) / len(differences) if differences else 0

        if avg_growth > 0:
            advice = (
                "Your user base is growing! Keep engaging users with fresh content and updates. "
                "Consider adding referral programs, marketing campaigns, and proactive customer support "
                "to maintain and boost this positive trend."
            )
        elif avg_growth == 0:
            advice = (
                "Your user growth seems stable but not increasing. Consider introducing new features, "
                "special promotions, or reaching out to existing users for feedback to spark renewed interest."
            )
        else:
            advice = (
                "It appears that growth has slowed down or declined. Consider implementing targeted marketing campaigns, "
                "improving user onboarding experiences, or launching loyalty rewards. Revisit your app's features and "
                "try to understand user pain points to encourage more sign-ups."
            )
    else:
        # Not enough data points, provide generic advice
        advice = (
            "Not enough data to analyze growth trends yet. Keep monitoring user metrics over time. "
            "As data accumulates, consider improvements and marketing efforts to grow your user base."
        )

    return image_base64, advice


import base64
import io
import matplotlib.pyplot as plt
from accounts.models import PropertyOwner, Client
from owners.models import Agent, House, Room

def generate_statistics_bar_chart():
    """
    Generates a bar graph showing the total counts of owners, agents, clients, houses, and rooms.
    Returns the base64-encoded image, and a dictionary of totals including overall total.
    """

    # Get the totals
    total_owners = PropertyOwner.objects.count()
    total_agents = Agent.objects.count()
    total_clients = Client.objects.count()
    total_houses = House.objects.count()
    total_rooms = Room.objects.count()

    # Prepare data
    categories = ["Owners", "Agents", "Clients", "Houses", "Rooms"]
    values = [total_owners, total_agents, total_clients, total_houses, total_rooms]

    # Calculate overall total
    overall_total = sum(values)

    # Create bar chart
    plt.figure(figsize=(8, 5))
    bars = plt.bar(categories, values, color=["#4dc9f6", "#f67019", "#f53794", "#537bc4", "#acc236"])
    plt.title("Statistics: Owners, Agents, Clients, Houses & Rooms")
    plt.xlabel("Category")
    plt.ylabel("Count")
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Add value labels on top of each bar
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2.0, height + 0.5, f'{int(height)}', ha='center', va='bottom', fontsize=9, color='black')

    # Save the figure into a bytes buffer
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    plt.close()

    # Encode the image to base64
    image_base64 = base64.b64encode(image_png).decode('utf-8')

    totals_info = {
        'owners': total_owners,
        'agents': total_agents,
        'clients': total_clients,
        'houses': total_houses,
        'rooms': total_rooms,
        'overall': overall_total
    }

    return image_base64, totals_info


import base64
import io
import matplotlib.pyplot as plt
from owners.models import House

def generate_houses_by_region_chart():
    """
    Generates a bar graph showing the number of houses in each region.
    Groups houses by region (case-sensitive) and counts them.
    Returns:
        image_base64 (str): Base64-encoded PNG image of the bar chart.
        region_counts (dict): { region_name: house_count, ... }
        advice (str): Advice based on highest and lowest house counts.
        total_houses (int): Total number of houses across all regions.
    """

    # Get all houses and group by region
    houses = House.objects.all()
    region_counts = {}
    for house in houses:
        # Access the region's name field instead of calling strip() on the region object
        region = house.region.name.strip() if (house.region and house.region.name) else "Unknown"
        region_counts[region] = region_counts.get(region, 0) + 1

    # If no houses, handle gracefully
    if not region_counts:
        image_base64 = ""
        advice = "No houses found. Consider expanding marketing efforts to attract property owners in all regions."
        total_houses = 0
        return image_base64, region_counts, advice, total_houses

    # Create bar chart
    regions = list(region_counts.keys())
    counts = list(region_counts.values())
    total_houses = sum(counts)

    # Create bar chart
    plt.figure(figsize=(10, 5))
    bars = plt.bar(regions, counts, color="#4dc9f6")
    plt.title("Number of Houses by Region")
    plt.xlabel("Region")
    plt.ylabel("Number of Houses")
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Add value labels on top of each bar
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2.0, height + 0.5, f'{int(height)}', ha='center', va='bottom', fontsize=9, color='black')

    # Save figure to buffer
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    plt.close()

    # Encode image to base64
    image_base64 = base64.b64encode(image_png).decode('utf-8')

    # Determine the region with the highest and lowest number of houses
    max_count = max(counts)
    min_count = min(counts)
    # Get the regions with max and min (if multiple, just pick one)
    max_region = [r for r, c in region_counts.items() if c == max_count]
    min_region = [r for r, c in region_counts.items() if c == min_count]

    # Generate advice
    if max_region and min_region:
        top = max_region[0]
        bottom = min_region[0]
        advice = (
            f"The region with the highest number of houses is {top} with {max_count} houses. "
            "Focus on maintaining quality and user satisfaction in this thriving region. "
            f"The region with the lowest number of houses is {bottom} with only {min_count} houses. "
            "Consider targeted marketing, improvements to infrastructure, or community outreach "
            "to attract more property owners to this underrepresented region."
        )
    else:
        advice = (
            "All houses are concentrated in a single region. Consider expanding into other regions "
            "to diversify the user base and increase accessibility."
        )

    return image_base64, region_counts, advice, total_houses


import base64
import io
import matplotlib.pyplot as plt
from owners.models import House

def generate_rooms_pie_chart():
    """
    Generates a pie chart showing the percentage of rooms in each region.
    We'll base this on the number of 'Room' objects per region.

    Returns:
        image_base64 (str): Base64-encoded PNG image of the pie chart
        advice (str): Advice based on distribution
        total_rooms (int): Total count of rooms across all regions
        rooms_per_region (dict): { region_name: room_count }
    """

    houses = House.objects.prefetch_related('rooms')
    rooms_per_region = {}

    # Aggregate room counts by region
    for house in houses:
        # Access region name correctly and strip it
        region = house.region.name.strip() if (house.region and house.region.name) else "Unknown"
        room_count = house.rooms.count()
        rooms_per_region[region] = rooms_per_region.get(region, 0) + room_count

    # If no rooms, handle gracefully
    if not rooms_per_region:
        image_base64 = ""
        advice = "No rooms found across regions."
        total_rooms = 0
        return image_base64, advice, total_rooms, rooms_per_region

    # Prepare data for pie chart
    regions = list(rooms_per_region.keys())
    counts = list(rooms_per_region.values())
    total_rooms = sum(counts)

    # Create pie chart
    plt.figure(figsize=(7,7))
    plt.pie(counts, labels=regions, autopct='%1.1f%%', startangle=90)
    plt.title("Percentage of Rooms by Region")
    plt.tight_layout()

    # Save figure to buffer
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    plt.close()

    # Encode to base64
    image_base64 = base64.b64encode(image_png).decode('utf-8')

    # Generate advice
    max_count = max(counts)
    min_count = min(counts)

    if len(regions) == 1:
        # Only one region present
        advice = (
            f"All rooms are concentrated in {regions[0]} with {total_rooms} rooms. "
            "Consider expanding properties to other regions for broader market reach."
        )
    else:
        max_regions = [r for r, c in rooms_per_region.items() if c == max_count]
        min_regions = [r for r, c in rooms_per_region.items() if c == min_count]

        if max_regions and min_regions:
            top = ', '.join(max_regions)
            bottom = ', '.join(min_regions)
            advice = (
                f"The region(s) with the highest room count: {top} ({max_count} rooms). "
                "Focus on maintaining quality and services in these leading regions. "
                f"The region(s) with the lowest room count: {bottom} ({min_count} rooms). "
                "Consider incentivizing property owners or improving local conditions to increase room availability."
            )
        else:
            # Generic fallback advice
            advice = (
                "Room distribution is mixed. Consider strategies tailored to each region's supply and demand."
            )

    return image_base64, advice, total_rooms, rooms_per_region
