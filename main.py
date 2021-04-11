import loader
from matplotlib import pyplot as plt
from tile import Tile
import numpy as np


def main():
    crop_types = loader.load_crop_types()

    for i in crop_types.iloc:
        if i['fall']:
            print(f'{i["name"]} grows in fall')

    player = loader.load_player()
    print(player)

    bonus = 1
    if player.profession == 'tiller':
        bonus = 1.1

    plt.style.use('ggplot')

    fig_cc, ax_cc = plt.subplots()
    fig_ex, ax_ex = plt.subplots()
    fig_ce, ax_ce = plt.subplots()
    fig_vic, ax_vic, = plt.subplots()
    fig_ose, ax_ose, = plt.subplots()

    on_season_end = []

    mask = crop_types[player.season]
    print(f'mask: {mask}')
    crop_types = crop_types[mask]

    for crop_type in crop_types.iloc:

        print('\n---------------------\n'
             f'crop: {crop_type["name"]} - {crop_type["daysToMature"]} days to mature')
        
        days = np.arange(1, 29)
        days_with_excess = []
        excess = []
        cumulative_earnings = np.zeros(28)
        crop_count = np.zeros(28)
        value_in_crops = np.zeros(28)

        # simulate if doesn't regrow
        if crop_type['regrowth'] == -1:

            can_afford = int(np.floor(player.seed_capital / crop_type['seedPrice']))
            tiles_count = min(can_afford, player.max_tiles)

            print(f'staring with {tiles_count} tiles')

            for i in days:
                print(f'day: {i}')

                if i < player.day_of_season:
                    print('\tpass')
                    continue

                # on harvest
                if (i % crop_type['daysToMature']) == 0:
                    print('\tharvest')

                    profit = tiles_count * crop_type['sellPrice'] * bonus

                    # can regrow till the end of season?
                    if 28 - i >= crop_type['daysToMature']:
                        seeds_got = int(tiles_count * crop_type['seedDrop'])
                        can_afford = int(profit / crop_type['seedPrice'])
                        can_plant_total = can_afford + seeds_got
                        will_plant = min(can_plant_total, player.max_tiles)
                        will_buy = max(will_plant - seeds_got, 0)

                        replant_cost = will_buy * crop_type['seedPrice']

                        profit -= replant_cost
                        if profit > 0:
                            excess.append(profit)
                            days_with_excess.append(i)

                        tiles_count = will_plant
                        print(f'\t{tiles_count} new crops')
                    else:
                        excess.append(profit)
                        days_with_excess.append(i)
                        print('\twill not finish regrowing')

                    cumulative_earnings[i - 1] += profit

                crop_count[i - 1] = tiles_count
                value_in_crops[i - 1] = crop_count[i - 1] * crop_type['seedPrice']

                # add earnings from proceding day
                if i > 1:
                    cumulative_earnings[i - 1] += cumulative_earnings[i - 2]

        # simulate if regrows
        if crop_type['regrowth'] > 0:

            can_afford = int(np.floor(player.seed_capital / crop_type['seedPrice']))
            tiles_count = min(can_afford, player.max_tiles)

            print(f'staring with {tiles_count} tiles, regrowth: {crop_type["regrowth"]}')
            
            tiles = [Tile(crop_type, 1)] * tiles_count

            for i in days:
                print(f'days: {i}')

                if i < player.day_of_season:
                    print('\tpass')
                    continue

                harvested = 0
                profit = 0
                for t in tiles:
                    if t.harvest_today(i):
                        harvested += 1
                        profit += crop_type['sellPrice']
                profit *= bonus
                print(f'\tharvested {harvested}')
                
                can_afford = int(profit / crop_type['seedPrice'])
                free_tiles = player.max_tiles - len(tiles)
                new_tile_count = min(free_tiles, can_afford)
                tiles += [Tile(crop_type, i)] * new_tile_count

                crop_count[i - 1] = len(tiles)
                value_in_crops[i - 1] = crop_count[i - 1] * crop_type['seedPrice']

                profit -= new_tile_count * crop_type['seedPrice']
                if profit > 0:
                    excess.append(profit)
                    days_with_excess.append(i)

                if i > 1:
                    cumulative_earnings[i - 1] = profit + cumulative_earnings[i - 2]
                else:
                    cumulative_earnings[i - 1] = 0

        # crop count
        ax_cc.plot(days, crop_count, marker='.', label=crop_type['name'])

        # excess gold on harvest
        ax_ex.scatter(days_with_excess, excess, marker='o', label=crop_type['name'])

        # cumulative earnings
        ax_ce.plot(days, cumulative_earnings, marker='.', label=crop_type['name'])
        on_season_end.append([int(cumulative_earnings[len(days) - 1]), str(crop_type['name'])])

        # value in crops
        ax_vic.plot(days, value_in_crops, marker='.', label=crop_type['name'])

    # draw charts

    # crop count
    ax_cc.set_title(f'crop count ({player.season})')
    ax_cc.set_xticks(days)
    ax_cc.set_xticklabels(days)
    ax_cc.set_xlabel('day')
    ax_cc.set_ylabel('number of crops')
    ax_cc.grid(True)
    # max crop count
    ax_cc.axline((0, player.max_tiles), (27, player.max_tiles),
               color='red', linestyle='--', label='max crop count')
    ax_cc.legend()

    # excess
    ax_ex.set_title(f'excess gold on harvest ({player.season})')
    ax_ex.set_xticks(days)
    ax_ex.set_xticklabels(days)
    ax_ex.set_xlabel('day')
    ax_ex.set_ylabel('excess gold on harvest [gold]')
    ax_ex.grid(True)
    ax_ex.legend()

    # cumulative earnings
    ax_ce.set_title(f'cumulative earnings ({player.season})')
    ax_ce.set_xticks(days)
    ax_ce.set_xticklabels(days)
    ax_ce.set_xlabel('day')
    ax_ce.set_ylabel('cumulative earnings [gold]')
    ax_ce.legend()

    # value in crops
    ax_vic.set_title(f'value in crops ({player.season})')
    ax_vic.set_xticks(days)
    ax_vic.set_xticklabels(days)
    ax_vic.set_xlabel('day')
    ax_vic.set_ylabel('value in crops [gold]')
    ax_vic.legend()

    # ROI
    tab = [(i['sellPrice'] / i['seedPrice'], i['name']) for i in crop_types.iloc]
    tab.sort()
    roi = [i[0] for i in tab]
    roi_names = [i[1] for i in tab]

    fig_roi, ax_roi = plt.subplots()

    ax_roi.barh(roi_names, roi)
    ax_roi.set_yticks(roi_names)
    ax_roi.set_yticklabels(roi_names)
    fig_roi.suptitle(f'crops ROI on first harvest ({player.season})')

    # on season end
    on_season_end.sort()
    ose_values = [i[0] for i in on_season_end]
    ose_names = [i[1] for i in on_season_end]
    print(ose_names)
    print(ose_values)
    ax_ose.barh(np.arange(len(crop_types)), ose_values)
    ax_ose.set_yticks(np.arange(len(crop_types)))
    ax_ose.set_yticklabels(ose_names)
    ax_ose.set_title(f'earnings on season\'s end with capital {player.seed_capital} gold ({player.season})')

    plt.tight_layout()

    # legent might be placed badly
    output = './out'
    fig_roi.savefig(f'{output}/roi.png')
    fig_cc.savefig(f'{output}/crop_count.png')
    fig_ex.savefig(f'{output}/excess.png')
    fig_ce.savefig(f'{output}/cumulative_earnigns.png')
    fig_vic.savefig(f'{output}/value_in_crops.png')
    fig_ose.savefig(f'{output}/on_seasaon_end.png')
    plt.show()


main()
