import gzip
import requests
import click


@click.command()
def relief():
  r = requests.get(
      'https://www.ngdc.noaa.gov/mgg/global/relief/ETOPO1/data/bedrock/grid_registered/netcdf/ETOPO1_Bed_g_gmt4.grd.gz', stream=True)
  r.raise_for_status()
  f = gzip.GzipFile(fileobj=r.raw)
  open('ETOPO1_Bed_g_gmt4.grd', 'wb').write(f.read())


if __name__ == '__main__':
  relief()
