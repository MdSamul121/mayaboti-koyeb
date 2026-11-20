import type { ReactNode } from "react";

import {
  configureChannel,
  disableMayabotiFeature,
  enableMayabotiFeature,
} from "@/lib/api";
import type { MayabotiChannelInstanceInfo, MayabotiFeatureInfo, MayabotiFeaturesPayload } from "@/lib/types";
import { useClient } from "@/providers/ClientProvider";
import {
  ChannelInstancesPanelView,
  type ChannelInstancesPanelCustomization,
  type ChannelInstancesPanelViewProps,
} from "./ChannelInstancesPanelView";

export type { ChannelInstancesPanelCustomization } from "./ChannelInstancesPanelView";

export function ChannelInstancesPanel({
  feature,
  showBrandLogos,
  instances,
  onFeaturesUpdate,
  customization,
  renderView,
}: {
  feature: MayabotiFeatureInfo;
  showBrandLogos: boolean;
  instances?: MayabotiChannelInstanceInfo[];
  onFeaturesUpdate: (payload: MayabotiFeaturesPayload) => void;
  customization?: ChannelInstancesPanelCustomization;
  renderView?: (props: ChannelInstancesPanelViewProps) => ReactNode;
}) {
  const { client } = useClient();
  const viewProps: ChannelInstancesPanelViewProps = {
    feature,
    showBrandLogos,
    instances,
    customization,
    onToggleInstance: async (instance, checked) => {
      const payload = checked
        ? await enableMayabotiFeature(client, feature.name, { instanceId: instance.id })
        : await disableMayabotiFeature(client, feature.name, { instanceId: instance.id });
      onFeaturesUpdate(payload);
    },
    onSaveInstance: async (instance, values) => {
      const payload = await configureChannel(client, feature.name, values, {
        enable: instance.enabled,
        instanceId: instance.id,
      });
      if (payload.mayaboti_features) onFeaturesUpdate(payload.mayaboti_features);
    },
  };
  return renderView ? renderView(viewProps) : <ChannelInstancesPanelView {...viewProps} />;
}
