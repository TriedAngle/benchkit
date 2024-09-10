import pathlib
import os
from typing import Optional, Iterable, List, Dict

from benchkit.benchkit.shell.shellasync import AsyncProcess
from benchkit.benchmark import Benchmark, CommandAttachment, PostRunHook, PreRunHook, RecordResult
from benchkit.campaign import CampaignSuite, CampaignCartesianProduct, Campaign
from benchkit.commandwrappers import CommandWrapper
from benchkit.commandwrappers.perf import PerfReportWrap, PerfStatWrap, enable_non_sudo_perf
from benchkit.platforms import Platform, get_current_platform
from benchkit.sharedlibs import SharedLib
from benchkit.utils.types import PathType


class ForgetFullException(Exception):
    pass

BUILD_VARIABLES = []
RUN_VARIABLES = []
TILT_VARIABELS = []

class IPCBenchmark(Benchmark):
    def __init__(
        self,
        bench_dir: PathType,
        command_wrappers: Iterable[CommandWrapper] = [],
        command_attachments: Iterable[CommandAttachment] = [],
        shared_libs: Iterable[SharedLib] = [],
        pre_run_hooks: Iterable[PreRunHook] = [],
        post_run_hooks: Iterable[PostRunHook] = [],
        platform: Platform | None = None,
    ) -> None:
        super().__init__(
            command_wrappers=command_wrappers,
            command_attachments=command_attachments,
            shared_libs=shared_libs,
            pre_run_hooks=pre_run_hooks,
            post_run_hooks=post_run_hooks,
        )
        self.bench_dir = bench_dir
        
        if platform is not None:
            self.platform = platform
        
    @property
    def bench_src_path(self) -> pathlib.Path:
        return self.bench_dir
    
    @staticmethod
    def get_build_var_names() -> List[str]:
        return BUILD_VARIABLES
    
    @staticmethod
    def get_run_var_names() -> List[str]:
        return RUN_VARIABLES
    
    @staticmethod
    def get_tilt_var_names() -> List[str]:
        return TILT_VARIABELS
    

    @staticmethod
    def _parse_results(
        output: str,
        nb_threads: int,
    ) -> Dict[str, str]:
        return {}
    

    def parse_output_to_results(
        self, 
        command_output: str, 
        build_variables: Dict[str, pathlib.Any], 
        run_variables: Dict[str, pathlib.Any], 
        benchmark_duration_seconds: int, 
        record_data_dir: pathlib.Path | pathlib.PathLike | str, 
        **kwargs
    ) -> Dict[str, pathlib.Any]:
        return super().parse_output_to_results(command_output, build_variables, run_variables, benchmark_duration_seconds, record_data_dir, **kwargs)
    

    def prebuild_bench(self, **kwargs) -> int:
        return super().prebuild_bench(**kwargs)
    
    def build_bench(self, **kwargs) -> None:
        return super().build_bench(**kwargs)
    
    def clean_bench(self) -> None:
        return super().clean_bench()
    
    def single_run(self, **kwargs) -> str | AsyncProcess:
        return super().single_run(**kwargs)
    


def main() -> None:
    bench_dir = "ipc-channel"
    nb_runs = 5,
    platform = get_current_platform()

    enable_non_sudo_perf(platform.comm)

    variables = {

    }

    VARIABLES_UNION = BUILD_VARIABLES + RUN_VARIABLES + TILT_VARIABELS

    for var in variables.keys():
        if var not in VARIABLES_UNION:
            raise ForgetFullException(f"Missing Variable definition: {var}")

    benchmark = IPCBenchmark(
        bench_dir=bench_dir,
        platform=platform,
    )

    campaign = CampaignCartesianProduct(
        name="IPC Benching",
        benchmark=benchmark,
        nb_runs=nb_runs,
        variables=variables,
        gdb=False,
        debug=False,
        constants=None,
        enable_data_dir=False,
    )

    campaigns: List[Campaign] = [campaign]
    suite = CampaignSuite(campaigns=campaigns)
    suite.print_durations()
    suite.run_suite()


if __name__ == "__main__":
    main()