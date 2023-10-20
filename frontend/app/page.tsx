import SimulationProgress from "@/components/overview/progress"
import VMCharts from "@/components/overview/vmcharts"
import VMStats from "@/components/overview/vmstats"

import Navbar from "@components/navbar"
import Sidebar from "@components/sidebar"

export default function Home() {
   return (
      <main>
         <Navbar />
         <div className="flex">
            <Sidebar />
            <div className="container space-y-16">
               <SimulationProgress />
               <VMStats />
               <VMCharts />
            </div>
         </div>
      </main>
   )
}
