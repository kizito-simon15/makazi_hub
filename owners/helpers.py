# owners/views.py
def build_houses_data(houses_qs):
    houses_data_list = []
    for house in houses_qs:
        combined_media = []
        # Use house.updates.all() if that’s your real model:
        for upd in house.updates.all():
            combined_media.append({
                'type': 'photo' if upd.update_type == 'photo' else 'video',
                'file': upd.update_file.url,
                'caption': upd.caption or ""
            })
        
        total_rooms = house.rooms.count()
        occupied = house.rooms.filter(availability_status="Occupied").count()
        available = total_rooms - occupied

        houses_data_list.append({
            'house': house,
            'media': combined_media,
            'available_rooms': available,
            'occupied_rooms': occupied,
        })
    return houses_data_list
