import VMCharts from "@/components/vmcharts"
import VMStats from "@/components/vmstats"

import Navbar from "@components/navbar"
import Sidebar from "@components/sidebar"

export default function Home() {
   return (
      <main>
         <Navbar />
         <div className="flex">
            <Sidebar />
            <div className="container">
               <VMStats />
               <VMCharts />
            </div>
         </div>
      </main>
   )
}
