import React from "react";
import renderer, { act } from "react-test-renderer";
import {
  Button,
  Text,
  TextInput,
  Card,
  ListItem,
  Badge,
  Chip,
  Skeleton,
  Spinner,
  EmptyState,
  ErrorState,
  Divider,
  Switch,
  Checkbox,
} from "../components/ui";

describe("UI Core Kit Smoke Tests", () => {
  it("renders Button", () => {
    let tree;
    act(() => {
      tree = renderer.create(<Button title="Click me" onPress={() => {}} />).toJSON();
    });
    expect(tree).toBeDefined();
  });

  it("renders Text", () => {
    let tree;
    act(() => {
      tree = renderer.create(<Text variant="h1">Heading 1</Text>).toJSON();
    });
    expect(tree).toBeDefined();
  });

  it("renders TextInput", () => {
    let tree;
    act(() => {
      tree = renderer.create(<TextInput label="Email" placeholder="user@example.com" />).toJSON();
    });
    expect(tree).toBeDefined();
  });

  it("renders Card and ListItem", () => {
    let card;
    act(() => {
      card = renderer
        .create(
          <Card>
            <ListItem title="Masjid Taqwa" subtitle="Dehradun" />
          </Card>
        )
        .toJSON();
    });
    expect(card).toBeDefined();
  });

  it("renders Badge and Chip", () => {
    let badge, chip;
    act(() => {
      badge = renderer.create(<Badge label="Featured" />).toJSON();
      chip = renderer.create(<Chip label="Parking" selected />).toJSON();
    });
    expect(badge).toBeDefined();
    expect(chip).toBeDefined();
  });

  it("renders Skeleton and Spinner", () => {
    let skeleton, spinner;
    act(() => {
      skeleton = renderer.create(<Skeleton width={100} height={20} />).toJSON();
      spinner = renderer.create(<Spinner />).toJSON();
    });
    expect(skeleton).toBeDefined();
    expect(spinner).toBeDefined();
  });

  it("renders EmptyState and ErrorState", () => {
    let empty, error;
    act(() => {
      empty = renderer
        .create(<EmptyState title="No masjids" description="Try another location" />)
        .toJSON();
      error = renderer
        .create(<ErrorState message="Failed to load" onRetry={() => {}} />)
        .toJSON();
    });
    expect(empty).toBeDefined();
    expect(error).toBeDefined();
  });

  it("renders Switch and Checkbox", () => {
    let sw, cb;
    act(() => {
      sw = renderer
        .create(<Switch value={true} onValueChange={() => {}} label="Notifications" />)
        .toJSON();
      cb = renderer
        .create(<Checkbox checked={true} onCheckedChange={() => {}} label="Remember me" />)
        .toJSON();
    });
    expect(sw).toBeDefined();
    expect(cb).toBeDefined();
  });

  it("renders Divider", () => {
    let divider;
    act(() => {
      divider = renderer.create(<Divider />).toJSON();
    });
    expect(divider).toBeDefined();
  });
});
