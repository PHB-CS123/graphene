import argparse
from os import path

from tests_e2e.benchmarks.benchmark import Benchmark
from graphene.utils.pretty_printer import PrettyPrinter

FIXTURE_SUFFIX = "-fixture"


def get_argument_parser():
    h_filename = "The .gp file to set up the database with (must have suffix " \
                 "'%s'), as well as the .gp file to benchmark this " \
                 "fixture with. Every fixture must have a benchmark file." \
                 % FIXTURE_SUFFIX
    parser = argparse.ArgumentParser()
    parser.add_argument("filenames",
                        help=h_filename,
                        type=str,
                        nargs="*")
    parser.add_argument("-o", "--output",
                        help="the file to output the benchmarks results to.",
                        type=str,
                        default=None)
    return parser


def print_results(header, results, output):
    if not output:
        p = PrettyPrinter()
        p.print_info(header)
        p.print_table(results.items(), header=["Command", "Time"])
    else:
        PrettyPrinter.NO_COLORS = True
        p = PrettyPrinter()
        f = open(output, "a")
        p.print_info(header, output=f)
        p.print_table(results.items(), header=["Command", "Time"], output=f)


def filter_filenames_and_fixtures(filenames):
    # Map of fixture base filenames to a tuple containing the full fixture
    # filename and benchmark for that fixture
    fixture_benchmark_map = {}
    # Benchmarks thar are not yet matched to their fixtures. Maps fixture
    # base filenames to benchmark filenames
    rem_benchmarks = {}
    for filename, base_name in zip(filenames, map(path.basename, filenames)):
        # Fixture
        if base_name.find(FIXTURE_SUFFIX) != -1:
            if filename in fixture_benchmark_map:
                raise ValueError("Duplicate fixture filename: %s" % filename)
            fixture_benchmark_map[base_name] = (filename, None)
        # Must be a benchmark
        else:
            fixture_name = base_name.replace(".", "%s." % FIXTURE_SUFFIX)
            try:
                fix_path = fixture_benchmark_map[fixture_name][0]
                fixture_benchmark_map[fixture_name] = (fix_path, filename)
            # Fixture has not yet been processed
            except KeyError:
                rem_benchmarks[fixture_name] = filename
    # All files are processed at this point, map remaining benchmarks
    for fixture_basename, benchmark_path in rem_benchmarks.items():
        try:
            fix_path = fixture_benchmark_map[fixture_basename][0]
            fixture_benchmark_map[fixture_basename] = (fix_path, benchmark_path)
        except KeyError:
            raise ValueError("No fixture exists for benchmark path: %s"
                             % benchmark_path)
    # Make sure all fixtures have benchmarks, leave map in terms of full paths
    full_paths_map = {}
    for fixture, fix_bench_tup in fixture_benchmark_map.items():
        full_fix_path, benchmark_path = fix_bench_tup
        if benchmark_path is None:
            raise ValueError("No benchmark exists for fixture: %s" % fixture)
        full_paths_map[full_fix_path] = benchmark_path
    return full_paths_map

if __name__ == '__main__':
    # Parse command line arguments
    args = get_argument_parser().parse_args()
    fix_benchmarks_paths = filter_filenames_and_fixtures(args.filenames)
    for fixture_path, benchmark_path in fix_benchmarks_paths.items():
        b = Benchmark(fixture_path, benchmark_path)
        h = "Fixture: %s\nBenchmark: %s\n" % (fixture_path, benchmark_path)
        print_results(h, b.execute(), args.output)
        b.clean_up()
