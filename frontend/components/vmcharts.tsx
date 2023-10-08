import { Card, CardContent } from "@/components/ui/card"
import {
   Menubar,
   MenubarContent,
   MenubarItem,
   MenubarMenu,
} from "@/components/ui/menubar"
import { MyAreaGraph } from "@components/charts/areagraph"
import { MyBarChart } from "@components/charts/barchart"

/* Start sample data for bar charts and area charts */
import { useApiUrl, useCustom } from "@refinedev/core"
import dayjs from "dayjs"

interface Datum {
   date: string
   value: string
}
interface Chart {
   data: Datum[]
   total: number
   trend: number
}
const query = {
   start: dayjs().subtract(7, "days").startOf("day"),
   end: dayjs().startOf("day"),
}
/* End sample data for bar charts and area charts */

export default function VMCharts() {
   /* Start sample data for bar charts and area charts */
   const API_URL = useApiUrl()

   const { data: dailyRevenue } = useCustom<Chart>({
      url: `${API_URL}/dailyRevenue`,
      method: "get",
      config: {
         query,
      },
   })

   const { data: dailyOrders } = useCustom<Chart>({
      url: `${API_URL}/dailyOrders`,
      method: "get",
      config: {
         query,
      },
   })

   const { data: newCustomers } = useCustom<Chart>({
      url: `${API_URL}/newCustomers`,
      method: "get",
      config: {
         query,
      },
   })
   /* End sample data for bar charts and area charts */

   {
      /* Some Charts with performance info */
   }
   return (
      <Card className="p-5">
         <Menubar>
            <MenubarMenu>
               <MenubarContent aria-label="Options" className="gap-0">
                  {/* Revenue chart */}
                  <MenubarItem key="revenue" title="Revenue">
                     <Card>
                        <CardContent>
                           {/* TODO: - the data fields need to be filled with actual data */}
                           <MyAreaGraph
                              data={dailyRevenue?.data?.data ?? []}
                              stroke="#8884d8"
                              fill="#cfeafc"
                           />
                        </CardContent>
                     </Card>
                  </MenubarItem>
                  {/* Orders chart */}
                  <MenubarItem key="orders" title="Orders">
                     <Card>
                        <CardContent>
                           <MyBarChart
                              data={dailyOrders?.data?.data ?? []}
                              fill="#ffce90"
                           />
                        </CardContent>
                     </Card>
                  </MenubarItem>
                  {/* Customers chart */}
                  <MenubarItem key="customers" title="Customers">
                     <Card>
                        <CardContent>
                           <MyAreaGraph
                              data={newCustomers?.data?.data ?? []}
                              stroke="#00bd56"
                              fill="#ccf3f3"
                           />
                        </CardContent>
                     </Card>
                  </MenubarItem>
               </MenubarContent>
            </MenubarMenu>
         </Menubar>
      </Card>
   )
}
