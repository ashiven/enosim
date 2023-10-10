"use client"
import { Card, CardContent } from "@/components/ui/card"
import { MyAreaGraph } from "@/components/ui/charts/areagraph"
import { MyBarChart } from "@/components/ui/charts/barchart"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"

{
   /* TODO: - the data fields need to be filled with actual data */
}
export default function VMCharts() {
   return (
      <div className="container mx-auto mt-12 mb-8">
         <Card className="p-5">
            {/* Some Charts with performance info */}
            <Tabs defaultValue="revenue">
               <TabsList>
                  <TabsTrigger value="revenue">CPU Usage</TabsTrigger>
                  <TabsTrigger value="orders">RAM Usage</TabsTrigger>
                  <TabsTrigger value="customers">Network Usage</TabsTrigger>
               </TabsList>
               {/* Revenue chart */}
               <TabsContent value="revenue">
                  <Card>
                     <CardContent className="p-6">
                        <MyAreaGraph
                           data={[
                              { date: "2021-12-12", value: "20" },
                              { date: "2021-12-13", value: "30" },
                              { date: "2021-12-14", value: "40" },
                              { date: "2021-12-15", value: "30" },
                              { date: "2021-12-16", value: "35" },
                              { date: "2021-12-17", value: "50" },
                              { date: "2021-12-18", value: "50" },
                              { date: "2021-12-19", value: "40" },
                              { date: "2021-12-20", value: "30" },
                              { date: "2021-12-21", value: "25" },
                              { date: "2021-12-22", value: "60" },
                              { date: "2021-12-23", value: "50" },
                           ]}
                           stroke="#8884d8"
                           fill="#cfeafc"
                        />
                     </CardContent>
                  </Card>
               </TabsContent>
               {/* Orders chart */}
               <TabsContent value="orders">
                  <Card>
                     <CardContent className="p-6">
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
                  <Card>
                     <CardContent className="p-6">
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
