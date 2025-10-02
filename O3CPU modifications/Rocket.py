import m5
from m5.objects import *

# --- Create the System ---

system = System()
system.clk_domain = SrcClockDomain(clock = '1GHz', voltage_domain = VoltageDomain())
system.mem_mode = 'timing'
system.mem_ranges = [AddrRange('2GB')]
system.membus = SystemXBar()

# --- Create the Rocket-like MinorCPU ---

# First, define the list of functional units for Rocket's execute stage
class RocketFUPool(MinorFUPool):
    # MinorCPU requires MinorFU objects
    FUList = [
        MinorIntALU(),
        MinorIntMultDiv(),
        MinorMemFU(),
        MinorFloatFU()
    ]

cpu = MinorCPU()

# Set parameters based on Rocket's in-order pipeline
cpu.fetch1ToFetch2BufferSize = 1
cpu.fetch2ToDecodeBufferSize = 1
cpu.decodeToExecuteBufferSize = 1
cpu.executeToMemoryBufferSize = 1
cpu.memoryToWritebackBufferSize = 1

# Use a simple branch predictor to model Rocket's predictor
cpu.branchPred = LocalBP()

# Assign the functional units
cpu.executeFuncUnits = RocketFUPool()

# --- Create the Cache Hierarchy ---

system.cpu = cpu
# Rocket's default L1 caches are typically smaller than BOOM's
system.cpu.icache = L1ICache(size='16kB')
system.cpu.dcache = L1DCache(size='16kB')
system.cpu.icache.connectCPU(system.cpu)
system.cpu.dcache.connectCPU(system.cpu)

system.l2bus = L2XBar()
system.cpu.icache.connectBus(system.l2bus)
system.cpu.dcache.connectBus(system.l2bus)

system.l2cache = L2Cache(size='512kB') # Rocket typically has a smaller L2
system.l2cache.connectCPUSideBus(system.l2bus)
system.l2cache.connectMemSideBus(system.membus)

# --- Memory and Final Connections ---

system.system_port = system.membus.cpu_side_ports
system.mem_ctrl = MemCtrl()
system.mem_ctrl.dram = DDR4_2400_8x8()
system.mem_ctrl.port = system.membus.mem_side_ports

# --- Set up the process to run ---

# This should be a RISC-V executable, compiled with a RISC-V toolchain
# process = Process(cmd = ['path/to/riscv-executable'])
# system.cpu.workload = process
# system.cpu.createThreads()

# --- Instantiate and Run ---

root = Root(full_system = False, system = system)
m5.instantiate()

print("Beginning simulation of Rocket-like MinorCPU!")
exit_event = m5.simulate()
print(f"Exiting @ tick {m5.curTick()} because {exit_event.getCause()}")

