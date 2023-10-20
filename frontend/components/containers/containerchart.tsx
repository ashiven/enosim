"use client"
import { Card, CardContent } from "@/components/ui/card"
import { MyAreaGraph } from "@/components/ui/charts/areagraph"
import { MyLineChart } from "@/components/ui/charts/linechart"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"

export default function ContainerChart({ data }: any) {
   return (
      <div className="container mx-auto mt-12 mb-8">
         <Card className="p-5">
            <Tabs defaultValue="revenue">
               <TabsList>
                  <TabsTrigger value="cpu">CPU Usage</TabsTrigger>
                  <TabsTrigger value="ram">RAM Usage</TabsTrigger>
                  <TabsTrigger value="network">Network Usage</TabsTrigger>
               </TabsList>
               {/* CPU Usage */}
               <TabsContent value="cpu">
                  <Card>
                     <CardContent className="p-6">
                        <MyAreaGraph
                           data={data.cpuData}
                           stroke="#8884d8"
                           fill="#cfeafc"
                        />
                     </CardContent>
                  </Card>
               </TabsContent>
               {/* RAM Usage */}
               <TabsContent value="ram">
                  <Card>
                     <CardContent className="p-6">
                        <MyAreaGraph
                           data={data.ramData}
                           stroke="#00bd56"
                           fill="#ccf3f3"
                        />
                     </CardContent>
                  </Card>
               </TabsContent>
               {/* Network Usage */}
               <TabsContent value="network">
                  <Card>
                     <CardContent className="p-6">
                        <MyLineChart
                           data={data.netData}
                           fill1="#ffce90"
                           fill2="#82ca9d"
                        />
                     </CardContent>
                  </Card>
               </TabsContent>
            </Tabs>
         </Card>
      </div>
   )
}
