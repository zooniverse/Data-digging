import pandas
import matplotlib.pyplot as plt

# inputs
brids_over_time_path = 'all_birds_over_time.csv'

birds = pandas.read_csv(brids_over_time_path)
birds.date = pandas.to_datetime(birds.date, format='%Y-%m-%d %H:%M:%S')
birds.sort_values('date', inplace=True)

for ct, site in enumerate(birds.site.unique()):
    sdx = birds.site == site
    birds_site = birds[sdx]
    site_count = birds_site.groupby(birds_site.date.map(lambda x: x.strftime('%Y-%m-%d')))['kittiwakes', 'guillemots', 'chicks', 'others'].sum()

    fig = plt.figure(ct, figsize=(12, 8))
    ax1 = plt.subplot(211)
    ax2 = plt.subplot(212)
    date = pandas.to_datetime(site_count.index)
    ax1.plot(date, site_count.kittiwakes, 'C8', label='Kittiwakes')
    ax1.plot(date, site_count.guillemots, 'C0', label='Guillemots')
    ax2.plot(date, site_count.others, 'C3', label='Others')
    ax2.plot(date, site_count.chicks, 'C6', label='Chicks')
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Number')
    ax1.legend()
    ax2.set_xlabel('Date')
    ax2.set_ylabel('Number')
    ax2.legend()
    plt.tight_layout()
    plt.savefig('{0}_by_day.png'.format(site))
    plt.close(fig)
