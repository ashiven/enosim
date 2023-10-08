"use client"
import { Card, CardContent } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { MyAreaGraph } from "@components/charts/areagraph"
import { MyBarChart } from "@components/charts/barchart"

{
   /* TODO: - the data fields need to be filled with actual data */
}
export default function VMCharts() {
   return (
      <div className="p-5">
         <Card className="p-5">
            {/* Some Charts with performance info */}
            <Tabs defaultValue="revenue">
               <TabsList>
                  <TabsTrigger value="revenue">Revenue</TabsTrigger>
                  <TabsTrigger value="orders">Orders</TabsTrigger>
                  <TabsTrigger value="customers">Customers</TabsTrigger>
               </TabsList>
               {/* Revenue chart */}
               <TabsContent value="revenue">
                  Revenue
                  <Card>
                     <CardContent>
                        <MyAreaGraph
                           data={[
                              { date: "2021-12-12", value: "20" },
                              { date: "2021-12-13", value: "30" },
                              { date: "2021-12-14", value: "40" },
                              { date: "2021-12-15", value: "30" },
                              { date: "2021-12-16", value: "35" },
                              { date: "2021-12-17", value: "50" },
                           ]}
                           stroke="#8884d8"
                           fill="#cfeafc"
                        />
                     </CardContent>
                  </Card>
               </TabsContent>
               {/* Orders chart */}
               <TabsContent value="orders">
                  Orders
                  <Card>
                     <CardContent>
                        <MyBarChart
                           data={[
                              { date: "2021-12-12", value: "20" },
                              { date: "2021-12-13", value: "30" },
                              { date: "2021-12-14", value: "40" },
                              { date: "2021-12-15", value: "30" },
                              { date: "2021-12-16", value: "35" },
                              { date: "2021-12-17", value: "50" },
                           ]}
                           fill="#ffce90"
                        />
                     </CardContent>
                  </Card>
               </TabsContent>
               {/* Customers chart */}
               <TabsContent value="customers">
                  Customers
                  <Card>
                     <CardContent>
                        <MyAreaGraph
                           data={[
                              { date: "2021-12-12", value: "20" },
                              { date: "2021-12-13", value: "30" },
                              { date: "2021-12-14", value: "40" },
                              { date: "2021-12-15", value: "30" },
                              { date: "2021-12-16", value: "35" },
                              { date: "2021-12-17", value: "50" },
                           ]}
                           stroke="#00bd56"
                           fill="#ccf3f3"
                        />
                     </CardContent>
                  </Card>
               </TabsContent>
            </Tabs>
         </Card>
      </div>
   )
}
