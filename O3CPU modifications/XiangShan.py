import m5
from m5.objects import *

# --- Create the System ---

system = System()
system.clk_domain = SrcClockDomain(clock = '2GHz', voltage_domain = VoltageDomain())
system.mem_mode = 'timing'
system.mem_ranges = [AddrRange('4GB')]
system.membus = SystemXBar()

# --- Create the XiangShan-like O3 CPU ---

# Define the large and diverse functional unit pool for XiangShan
class XiangShanFUPool(FUPool):
    FUList = [
        IntALU(opLat=1), IntALU(opLat=1), IntALU(opLat=1), IntALU(opLat=1), IntALU(opLat=1), IntALU(opLat=1),
        IntMultDiv(opLat=3), IntMultDiv(opLat=3),
        FP_ALU(opLat=2), FP_ALU(opLat=2),
        ReadPort(), ReadPort(),
        WritePort()
    ]

cpu = O3CPU()

# Set parameters based on XiangShan "Nanhu" architecture
# Pipeline widths
cpu.fetchWidth = 8
cpu.decodeWidth = 6
cpu.renameWidth = 6
cpu.dispatchWidth = 6
cpu.issueWidth = 6
cpu.wbWidth = 6
cpu.commitWidth = 6

# Instruction window and buffer sizes
cpu.numROBEntries = 256
cpu.numIQEntries = 128
cpu.LQEntries = 72
cpu.SQEntries = 72

# Physical register files
cpu.numPhysIntRegs = 160
cpu.numPhysFloatRegs = 160

# Use a high-performance branch predictor
cpu.branchPred = TournamentBP()

# Assign the functional units
cpu.fuPool = XiangShanFUPool()

# --- Create the Cache Hierarchy (3-level for XiangShan) ---

system.cpu = cpu
# XiangShan has large 64kB L1 caches
system.cpu.icache = L1ICache(size='64kB')
system.cpu.dcache = L1DCache(size='64kB')
system.cpu.icache.connectCPU(system.cpu)
system.cpu.dcache.connectCPU(system.cpu)

system.l2bus = L2XBar()
system.cpu.icache.connectBus(system.l2bus)
system.cpu.dcache.connectBus(system.l2bus)

system.l2cache = L2Cache(size='1MB')
system.l2cache.connectCPUSideBus(system.l2bus)

# Create an L3 bus and cache
system.l3bus = L2XBar()
system.l2cache.connectMemSideBus(system.l3bus)
system.l3cache = L3Cache(size='8MB')
system.l3cache.connectCPUSideBus(system.l3bus)
system.l3cache.connectMemSideBus(system.membus)

# --- Memory and Final Connections ---

system.system_port = system.membus.cpu_side_ports
system.mem_ctrl = MemCtrl()
system.mem_ctrl.dram = DDR4_2400_8x8()
system.mem_ctrl.port = system.membus.mem_side_ports

# --- Set up the process to run ---

# This should be a RISC-V executable
# process = Process(cmd = ['path/to/riscv-executable'])
# system.cpu.workload = process
# system.cpu.createThreads()

# --- Instantiate and Run ---

root = Root(full_system = False, system = system)
m5.instantiate()

print("Beginning simulation of XiangShan-Nanhu-like O3CPU!")
exit_event = m5.simulate()
print(f"Exiting @ tick {m5.curTick()} because {exit_event.getCause()}")

