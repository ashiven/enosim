import VMCharts from "@/components/vmcharts"

import Navbar from "@components/navbar"
import Sidebar from "@components/sidebar"

export default function Home() {
   return (
      <main>
         <Navbar />
         <div className="flex">
            <Sidebar />
            <div className="container">
               <VMCharts />
            </div>
         </div>
      </main>
   )
}
