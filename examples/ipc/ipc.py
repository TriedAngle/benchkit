import pathlib
import os
from typing import Any, Optional, Iterable, List, Dict

from benchkit.shell.shellasync import AsyncProcess
from benchkit.benchmark import Benchmark, CommandAttachment, PostRunHook, PreRunHook, RecordResult
from benchkit.campaign import CampaignSuite, CampaignCartesianProduct, Campaign
from benchkit.commandwrappers import CommandWrapper
from benchkit.commandwrappers.perf import PerfReportWrap, PerfStatWrap, enable_non_sudo_perf
from benchkit.platforms import Platform, get_current_platform
from benchkit.sharedlibs import SharedLib
from benchkit.utils.types import PathType
from benchkit.hdc import OpenHarmonyDeviceConnector


class ForgetFullException(Exception):
    pass


MOBILE = False
SKIP_REBUILD = True

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
        hdc: OpenHarmonyDeviceConnector | None = None,
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

        if hdc is not None:
            self.hdc = hdc
    

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
    

    # @staticmethod
    # def _parse_results(
    #     output: str,
    #     nb_threads: int,
    # ) -> Dict[str, str]:
        # return {}
    

    def parse_output_to_results(
        self, 
        command_output: str, 
        build_variables: Dict[str, Any], 
        run_variables: Dict[str, Any], 
        benchmark_duration_seconds: int, 
        record_data_dir: PathType, 
        **kwargs
    ) -> Dict[str, Any]:
        return { "please": "fixme" }
    

    def prebuild_bench(self, **kwargs) -> None:
        if not MOBILE:
            return
        self.hdc

    def build_bench(self, **kwargs) -> None:
        if MOBILE:
            return
        
        if not SKIP_REBUILD:
            self.platform.comm.shell(
                command="cargo build",
                current_dir=self.bench_dir
            )
    
    def clean_bench(self) -> None:
        if MOBILE:
            return

        if not SKIP_REBUILD:
            self.platform.comm.shell(
                command="cargo clean",
                current_dir=self.bench_dir
            )
    
    def single_run(self, **kwargs) -> str:
        run_command: List[str]
        if MOBILE:
            run_command = [
                "./ipc_runner"
            ]
        else:
            run_command = [
                "cargo", "run", "--"
            ]

        wrapped_run_command, wrapped_environment = self._wrap_command(
            run_command=run_command,
            environment={},
            **kwargs,
        )

        output = self.run_bench_command(
            environment={},
            run_command=run_command,
            wrapped_run_command=wrapped_run_command,
            current_dir=self.bench_dir,
            wrapped_environment=wrapped_environment,
            print_output=False,
        )

        return output    


def main() -> None:
    nb_runs = 5

    bench_dir: str = "./examples/ipc/ipc_runner"
    if MOBILE:
        bench_dir = "/data/testing/ipc/"
   
    platform: Platform = None
    if not MOBILE:
        platform = get_current_platform()
        enable_non_sudo_perf(platform.comm)

    hdc: OpenHarmonyDeviceConnector | None = None
    if MOBILE:
        devices = OpenHarmonyDeviceConnector.query_devices()
        hdc = OpenHarmonyDeviceConnector(devices[0])

    variables = {

    }

    VARIABLES_UNION = BUILD_VARIABLES + RUN_VARIABLES + TILT_VARIABELS

    for var in variables.keys():
        if var not in VARIABLES_UNION:
            raise ForgetFullException(f"Missing Variable definition: {var}")

    benchmark = IPCBenchmark(
        bench_dir=bench_dir,
        platform=platform,
        hdc=hdc,
    )

    campaign = CampaignCartesianProduct(
        name="IPC Benching",
        benchmark=benchmark,
        nb_runs=nb_runs,
        variables=variables,
        gdb=False,
        debug=False,
        constants=None,
        enable_data_dir=True,
    )

    campaigns: List[Campaign] = [campaign]
    suite = CampaignSuite(campaigns=campaigns)
    # suite.print_durations()
    suite.run_suite()


if __name__ == "__main__":
    main()
