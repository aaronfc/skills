# Sender-name explanation experiment

Manual writing comparison for issue #3. Both versions use the facts in
`explain_sender_name_to_newcomer` and target a reader who understands email but
has never used WordPress. These are authored examples, not model-evaluation
results or a reader study.

## Ordinary plain English

When you change the sender name in settings, the next email now uses that name
without restarting the plugin. WordPress provides a filter, which lets plugin
code change a value before WordPress uses it. We use its standard sender-name
filter, `wp_mail_from_name`, and chose to read the saved setting each time an
email is prepared. The preview showed the new name, but real delivery was not
tested.

## Experimental wording

Change the sender name in settings, and the next email uses that name. You do
not need to restart the plugin. A WordPress filter lets plugin code change a
value before WordPress uses it. We use the standard sender-name filter,
`wp_mail_from_name`. We chose to read the saved setting each time an email is
prepared. The preview showed the new name. We did not test real delivery.

## Assessment and limits

Both examples preserve the behavior, explain the filter, distinguish the
standard interface from our choice, and retain the untested-delivery limit.
The experimental version separates the convention and choice into two
sentences. Its final sentence names who did not test delivery. The ordinary
version connects related facts more smoothly; the experimental version has
more short, repeated sentence openings. These are editorial judgments about
this sample, not measured improvements in comprehension.

The experiment borrows active voice, focused sentences, and consistent names.
[ASD-STE100](https://www.asd-ste100.org/assets/files/ASD-STE100_ISSUE9.pdf)
defines a broader specification, including a controlled dictionary; neither
example was checked for compliance. Recommendation: retain plain-English,
example-first guidance and test these principles without requiring the standard
or its vocabulary. The paired evaluation scenario makes that comparison
repeatable. Independent model evaluation and testing with unfamiliar readers
remain outstanding; this example does not establish general superiority.
