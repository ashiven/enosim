import VMCharts from "@/components/vmcharts"
import VMStats from "@/components/vmstats"

import Navbar from "@components/navbar"
import Sidebar from "@components/sidebar"

export default function Home() {
   return (
      <main className="">
         <Navbar />
         <div className="flex">
            <Sidebar />
            <div className="">
               <VMStats />
               <VMCharts />
            </div>
         </div>
      </main>
   )
}
